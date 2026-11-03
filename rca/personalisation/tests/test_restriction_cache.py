from unittest.mock import patch

from django.db import transaction
from django.test import TestCase, override_settings
from wagtail.contrib.frontend_cache.utils import purge_url_from_cache
from wagtail.models import Page, PageViewRestriction, Site

from rca.home.models import HomePage
from rca.personalisation.tests.test_integration import InformationPageFactory


@override_settings(
    WAGTAILFRONTENDCACHE={
        "default": {
            "BACKEND": "rca.utils.frontend_cache.CloudflareBackend",
            "EMAIL": "cache@example.com",
            "TOKEN": "test-cache-key",
            "ZONEID": "test-zone",
        }
    }
)
class RestrictionCacheTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.home = HomePage.objects.first()
        cls.page = InformationPageFactory(parent=cls.home, slug="restricted-section")
        cls.child = InformationPageFactory(parent=cls.page, slug="child")
        cls.sibling = InformationPageFactory(parent=cls.home, slug="unrelated")
        site = Site.objects.get(is_default_site=True)
        site.hostname = "www.rca.ac.uk"
        site.port = 443
        site.save()

    def setUp(self):
        patcher = patch("requests.post")
        self.post = patcher.start()
        self.addCleanup(patcher.stop)
        self.post.return_value.json.return_value = {"success": True}

    def assert_section_purged(self):
        self.post.assert_called_once_with(
            "https://api.cloudflare.com/client/v4/zones/test-zone/purge_cache",
            json={"prefixes": ["www.rca.ac.uk/restricted-section/"]},
            headers={
                "X-Auth-Email": "cache@example.com",
                "X-Auth-Key": "test-cache-key",
                "Content-Type": "application/json",
            },
            timeout=10,
        )

    def test_adding_restriction_purges_page_descendants_and_query_variants(self):
        self.assertIn("public", self.client.get(self.child.url)["Cache-Control"])

        with self.captureOnCommitCallbacks(execute=True):
            PageViewRestriction.objects.create(
                page=self.page, restriction_type="password", password="test-password"
            )
            self.post.assert_not_called()

        # A prefix purge includes descendants and query strings, unlike file purges.
        self.assert_section_purged()
        for page in [self.page, self.child]:
            response = self.client.get(page.url)
            self.assertNotContains(response, 'data-personalisation-url="')
        self.assertIn("public", self.client.get(self.sibling.url)["Cache-Control"])

    def test_editing_and_removing_restriction_purges_after_commit(self):
        restriction = PageViewRestriction.objects.create(
            page=self.page, restriction_type="password", password="test-password"
        )
        for action in ["edit", "delete"]:
            with self.subTest(action=action):
                with self.captureOnCommitCallbacks(execute=True):
                    if action == "edit":
                        restriction.password = "changed-password"
                        restriction.save()
                    else:
                        restriction.delete()
                    self.post.assert_not_called()
                self.assert_section_purged()
                self.post.reset_mock()

    def test_rolled_back_restriction_does_not_purge(self):
        with self.captureOnCommitCallbacks(execute=True):
            try:
                with transaction.atomic():
                    PageViewRestriction.objects.create(
                        page=self.page,
                        restriction_type="login",
                    )
                    raise ValueError("Roll back the restriction")
            except ValueError:
                pass
        self.post.assert_not_called()

    def test_all_hostnames_serving_the_subtree_are_purged(self):
        Site.objects.create(hostname="another.rca.ac.uk", port=443, root_page=self.home)
        Site.objects.create(hostname="child.rca.ac.uk", port=443, root_page=self.child)
        Site.objects.create(
            hostname="unrelated.rca.ac.uk", port=443, root_page=self.sibling
        )
        with self.captureOnCommitCallbacks(execute=True):
            PageViewRestriction.objects.create(page=self.page, restriction_type="login")

        self.assertEqual(
            self.post.call_args.kwargs["json"],
            {
                "prefixes": [
                    "another.rca.ac.uk/restricted-section/",
                    "child.rca.ac.uk/",
                    "www.rca.ac.uk/restricted-section/",
                ]
            },
        )

    def test_restriction_above_site_root_purges_the_entire_site(self):
        with self.captureOnCommitCallbacks(execute=True):
            PageViewRestriction.objects.create(
                page=Page.get_first_root_node(), restriction_type="login"
            )
        self.assertEqual(
            self.post.call_args.kwargs["json"],
            {"prefixes": ["www.rca.ac.uk/"]},
        )

    @override_settings(WAGTAILFRONTENDCACHE={})
    def test_no_backend_does_not_contact_cloudflare(self):
        with self.captureOnCommitCallbacks(execute=True):
            PageViewRestriction.objects.create(page=self.page, restriction_type="login")
        self.post.assert_not_called()

    def test_existing_page_purges_still_use_the_file_api(self):
        purge_url_from_cache(self.page.full_url)
        self.assertEqual(
            self.post.call_args.kwargs["json"], {"files": [self.page.full_url]}
        )

    @patch("rca.utils.frontend_cache.logger")
    def test_cloudflare_failure_is_logged(self, logger):
        self.post.return_value.json.return_value = {"success": False}
        with self.captureOnCommitCallbacks(execute=True):
            PageViewRestriction.objects.create(page=self.page, restriction_type="login")
        logger.error.assert_called_once()

    @override_settings(
        WAGTAILFRONTENDCACHE={
            "default": {
                "BACKEND": "rca.utils.frontend_cache.CloudflareBackend",
                "BEARER_TOKEN": "test-bearer-token",
                "ZONEID": "test-zone",
                "HOSTNAMES": ["another.rca.ac.uk"],
            }
        }
    )
    def test_backend_hostname_filter_and_bearer_token_are_respected(self):
        Site.objects.create(hostname="another.rca.ac.uk", port=443, root_page=self.home)
        with self.captureOnCommitCallbacks(execute=True):
            PageViewRestriction.objects.create(page=self.page, restriction_type="login")
        self.assertEqual(
            self.post.call_args.kwargs["json"],
            {"prefixes": ["another.rca.ac.uk/restricted-section/"]},
        )
        self.assertEqual(
            self.post.call_args.kwargs["headers"],
            {
                "Content-Type": "application/json",
                "Authorization": "Bearer test-bearer-token",
            },
        )
