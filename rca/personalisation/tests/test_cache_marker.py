import hashlib
import hmac
import json
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.urls import path, reverse
from wagtail.models import PageViewRestriction

from rca.home.models import HomePage
from rca.personalisation.tests.test_deferred_ctas import FormPageFactory
from rca.personalisation.tests.test_integration import InformationPageFactory
from rca.urls import urlpatterns as site_urlpatterns
from rca.users.factories import UserFactory


def sso_callback(request):
    # Exercise the same Django login operation used by social-auth, without OAuth.
    login(
        request,
        UserFactory(is_staff=True),
        backend="social_core.backends.azuread_tenant.AzureADTenantOAuth2",
    )
    return HttpResponse()


urlpatterns = [path("test-sso-callback/", sso_callback, name="test_sso_callback")]
urlpatterns += site_urlpatterns


@override_settings(
    PERSONALISATION_CACHE_SIGNING_KEY="test-only-anonymous-cache-signing-key",
    PERSONALISATION_CACHE_HOSTNAME="www.rca.ac.uk",
    ALLOWED_HOSTS=["www.rca.ac.uk", "beta.rca.ac.uk"],
)
class AnonymousCacheMarkerTests(TestCase):
    cookie_name = "__Host-rca-anonymous"

    @classmethod
    def setUpTestData(cls):
        cls.page = InformationPageFactory(parent=HomePage.objects.first())
        cls.user = UserFactory(is_staff=True, is_superuser=True)
        cls.user.set_password("test-password")
        cls.user.save()

    def get(self, url):
        return self.client.get(url, secure=True, headers={"host": "www.rca.ac.uk"})

    def fragment(self):
        return self.get(reverse("personalisation_ctas", args=[self.page.pk]))

    def assert_marker(self, response, now):
        cookie = response.cookies[self.cookie_name]
        version, expires, signature = cookie.value.split(".")
        self.assertEqual(version, "v1")
        self.assertGreater(int(expires), now)
        self.assertLessEqual(int(expires), now + 3600)
        message = (
            "rca-anonymous-cache:v1\nwww.rca.ac.uk\n"
            f"{self.client.cookies[settings.SESSION_COOKIE_NAME].value}\n{expires}"
        )
        expected = hmac.new(
            settings.PERSONALISATION_CACHE_SIGNING_KEY.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()
        self.assertEqual(signature, expected)
        self.assertTrue(cookie["secure"])
        self.assertTrue(cookie["httponly"])
        self.assertEqual(cookie["samesite"], "Lax")
        self.assertEqual(cookie["path"], "/")
        self.assertEqual(cookie["domain"], "")

    @patch("rca.personalisation.cache.time.time", return_value=1800000000)
    def test_first_visit_fragment_and_returning_page(self, mocked_time):
        first = self.get(self.page.url)
        self.assertEqual(first["X-RCA-Cacheable"], "public-v1")
        self.assertFalse(first.cookies)

        fragments = self.fragment()
        self.assert_marker(fragments, mocked_time.return_value)
        self.assertIn("no-store", fragments["Cache-Control"])
        self.assertNotIn("X-RCA-Cacheable", fragments)
        session_id = self.client.cookies[settings.SESSION_COOKIE_NAME].value

        returning = self.get(self.page.url)
        self.assertEqual(returning.content, first.content)
        self.assertEqual(returning["X-RCA-Cacheable"], "public-v1")
        self.assertFalse(returning.cookies)
        self.assertEqual(
            self.client.cookies[settings.SESSION_COOKIE_NAME].value, session_id
        )
        self.assertEqual(self.client.session["visit_count"][0]["count"], 1)

    @patch("rca.personalisation.cache.time.time", return_value=1800000000)
    def test_existing_anonymous_session_keeps_history_and_gets_marker(
        self, mocked_time
    ):
        self.fragment()
        del self.client.cookies[self.cookie_name]
        response = self.fragment()
        self.assert_marker(response, mocked_time.return_value)
        self.assertEqual(self.client.session["visit_count"][0]["count"], 2)

    def test_login_rotates_session_and_removes_anonymous_marker(self):
        self.fragment()
        old_session = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        old_marker = self.client.cookies[self.cookie_name].value
        response = self.client.post(
            reverse("wagtailcore_login"),
            {"username": self.user.username, "password": "test-password"},
            secure=True,
            headers={"host": "www.rca.ac.uk"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)
        self.assertNotEqual(
            self.client.cookies[settings.SESSION_COOKIE_NAME].value, old_session
        )
        self.assertEqual(response.cookies[self.cookie_name]["max-age"], 0)
        self.assertNotEqual(self.client.cookies[self.cookie_name].value, old_marker)
        self.assertNotIn("X-RCA-Cacheable", response)
        self.assertIn("no-store", response["Cache-Control"])

        page = self.get(self.page.url)
        self.assertNotIn("X-RCA-Cacheable", page)
        self.assertIn("private", page["Cache-Control"])
        fragments = self.fragment()
        self.assertNotIn(self.cookie_name, fragments.cookies)

    @override_settings(ROOT_URLCONF=__name__)
    def test_sso_login_also_rotates_session_and_clears_marker(self):
        self.fragment()
        old_session = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        response = self.get(reverse("test_sso_callback"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("azuread", self.client.session["_auth_user_backend"])
        self.assertNotEqual(
            self.client.cookies[settings.SESSION_COOKIE_NAME].value, old_session
        )
        self.assertEqual(response.cookies[self.cookie_name]["max-age"], 0)
        self.assertIn("no-store", response["Cache-Control"])

    def test_logout_does_not_issue_marker_on_redirect(self):
        self.client.force_login(
            self.user, backend="django.contrib.auth.backends.ModelBackend"
        )
        response = self.client.post(
            reverse("wagtailcore_logout"),
            secure=True,
            headers={"host": "www.rca.ac.uk"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertNotIn(self.cookie_name, response.cookies)
        fragments = self.fragment()
        self.assertIn(self.cookie_name, fragments.cookies)

    def test_errors_and_non_fragment_responses_do_not_issue_marker(self):
        for url in [
            reverse("personalisation_ctas", args=[2147483647]),
            reverse("wagtailcore_login"),
        ]:
            with self.subTest(url=url):
                response = self.get(url)
                self.assertNotIn(self.cookie_name, response.cookies)
                self.assertNotIn("X-RCA-Cacheable", response)

    def test_form_and_restricted_pages_never_opt_in_to_shared_caching(self):
        form = FormPageFactory(parent=HomePage.objects.first())
        restricted = InformationPageFactory(
            parent=HomePage.objects.first(), title="Restricted cache test"
        )
        PageViewRestriction.objects.create(
            page=restricted, restriction_type="password", password="test-password"
        )
        for page in [form, restricted]:
            with self.subTest(page=page.title):
                response = self.get(page.url)
                self.assertNotIn("X-RCA-Cacheable", response)
                self.assertNotIn(self.cookie_name, response.cookies)

    def test_private_fragment_renews_an_expired_marker(self):
        with patch("rca.personalisation.cache.time.time", return_value=1800000000):
            self.fragment()
        old_marker = self.client.cookies[self.cookie_name].value
        with patch("rca.personalisation.cache.time.time", return_value=1800003601):
            response = self.fragment()
            self.assert_marker(response, 1800003601)
        self.assertNotEqual(response.cookies[self.cookie_name].value, old_marker)
        self.assertEqual(self.client.session["visit_count"][0]["count"], 2)

    def test_host_and_https_are_required(self):
        for host, secure in [("beta.rca.ac.uk", True), ("www.rca.ac.uk", False)]:
            with self.subTest(host=host, secure=secure):
                response = self.client.get(
                    reverse("personalisation_ctas", args=[self.page.pk]),
                    secure=secure,
                    headers={"host": host},
                )
                self.assertNotIn(self.cookie_name, response.cookies)
                page = self.client.get(
                    self.page.url, secure=secure, headers={"host": host}
                )
                self.assertNotIn("X-RCA-Cacheable", page)

    @override_settings(PERSONALISATION_CACHE_SIGNING_KEY="")
    def test_missing_secret_leaves_feature_disabled(self):
        response = self.fragment()
        self.assertNotIn(self.cookie_name, response.cookies)
        self.assertNotIn("X-RCA-Cacheable", self.get(self.page.url))

    @patch("rca.personalisation.cache.time.time", return_value=1800000000)
    def test_marker_does_not_outlive_session(self, mocked_time):
        self.fragment()
        session = self.client.session
        session.set_expiry(120)
        session.save()
        response = self.fragment()
        self.assertEqual(response.cookies[self.cookie_name]["max-age"], 120)
        self.assertEqual(
            response.cookies[self.cookie_name].value.split(".")[1], "1800000120"
        )

    def test_shared_python_and_worker_signature_fixture(self):
        from rca.personalisation.cache import sign_anonymous_session

        fixture = json.loads(
            (Path(__file__).parent / "fixtures" / "anonymous_cache.json").read_text()
        )
        with override_settings(PERSONALISATION_CACHE_SIGNING_KEY=fixture["secret"]):
            self.assertEqual(
                sign_anonymous_session(
                    fixture["session"], fixture["hostname"], fixture["expires"]
                ),
                fixture["token"],
            )
