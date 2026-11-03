import json
import secrets
import subprocess
from pathlib import Path

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from wagtail.models import PageViewRestriction

from rca.home.models import HomePage
from rca.personalisation.tests.test_deferred_ctas import FormPageFactory
from rca.personalisation.tests.test_integration import InformationPageFactory
from rca.users.factories import UserFactory


@override_settings(
    PERSONALISATION_CACHE_HOSTNAME="www.rca.ac.uk",
    ALLOWED_HOSTS=["www.rca.ac.uk"],
)
class WorkerContractTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.page = InformationPageFactory(parent=HomePage.objects.first())

    def setUp(self):
        self.secret = secrets.token_hex(32)
        self.enterContext(
            override_settings(PERSONALISATION_CACHE_SIGNING_KEY=self.secret)
        )

    def get(self, url):
        return self.client.get(url, secure=True, headers={"host": "www.rca.ac.uk"})

    def worker_case(self, response, *, cookie="", url=None):
        headers = list(response.items())
        headers.extend(
            ("Set-Cookie", cookie.OutputString())
            for cookie in response.cookies.values()
        )
        return {
            "url": url or response.wsgi_request.build_absolute_uri(),
            "cookie": cookie,
            "response": {
                "status": response.status_code,
                "headers": headers,
                "body": response.content.decode(),
            },
        }

    def run_worker(self, cases):
        script = (
            Path(settings.BASE_DIR)
            / "infrastructure/cloudflare/tests/django-contract.mjs"
        )
        result = subprocess.run(
            ["node", str(script)],
            input=json.dumps({"secret": self.secret, "cases": cases}),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_real_public_headers_allow_cache_reuse(self):
        first = self.get(self.page.url)
        results = self.run_worker([self.worker_case(first), self.worker_case(first)])
        self.assertEqual([result["decision"] for result in results], ["MISS", "HIT"])
        self.assertEqual(results[-1]["originRequests"], 1)
        self.assertEqual(results[-1]["cacheEntries"], 1)
        self.assertEqual(results[-1]["body"], first.content.decode())

    @override_settings(
        CACHE_CONTROL_S_MAXAGE=42, CACHE_CONTROL_STALE_WHILE_REVALIDATE=0
    )
    def test_real_headers_with_a_different_cache_lifetime_are_accepted(self):
        page = self.get(self.page.url)
        results = self.run_worker([self.worker_case(page), self.worker_case(page)])
        self.assertEqual([result["decision"] for result in results], ["MISS", "HIT"])

    def test_real_private_responses_cannot_populate_the_public_cache(self):
        home = HomePage.objects.first()
        form = FormPageFactory(parent=home)
        restricted = InformationPageFactory(parent=home, title="Private contract page")
        PageViewRestriction.objects.create(
            page=restricted, restriction_type="password", password="test-password"
        )
        responses = [
            self.get(reverse("personalisation_ctas", args=[self.page.pk])),
            self.get(form.url),
            self.get(restricted.url),
        ]
        self.client.force_login(UserFactory(is_staff=True, is_superuser=True))
        responses.append(self.get(self.page.url))

        # Use a cache-eligible request to exercise response checks, not route or
        # session bypasses, with the real headers and Set-Cookie values intact.
        url = responses[-1].wsgi_request.build_absolute_uri()
        results = self.run_worker(
            [self.worker_case(response, url=url) for response in responses]
        )
        self.assertEqual(
            [result["decision"] for result in results], ["BYPASS-RESPONSE"] * 4
        )
        self.assertEqual(results[-1]["cacheEntries"], 0)
        self.assertEqual(results[-1]["originRequests"], 4)
