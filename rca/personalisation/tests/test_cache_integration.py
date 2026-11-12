from django.contrib.auth import get_user_model
from django.test import TestCase

from rca.home.models import HomePage
from rca.standardpages.models import InformationPage

User = get_user_model()


class PublicCacheVaryCookieIntegrationTest(TestCase):
    """
    Exercises PublicCacheVaryCookieMiddleware through the real MIDDLEWARE
    stack (SessionMiddleware, CsrfViewMiddleware, AuthenticationMiddleware,
    etc.) via the Django test client, rather than a stubbed get_response.
    This is what would catch a regression to middleware ordering in
    rca.settings.base.MIDDLEWARE, which the unit tests in test_middleware.py
    can't see since they instantiate the middleware in isolation.
    """

    def setUp(self):
        home_page = HomePage.objects.first()
        self.test_page = InformationPage(
            title="Cache Test Page",
            introduction="Test introduction",
        )
        home_page.add_child(instance=self.test_page)

    def test_anonymous_visitor_gets_a_shareable_cached_response(self):
        response = self.client.get(
            self.test_page.url, headers={"user-agent": "Mozilla/5.0"}
        )

        self.assertIn("public", response.get("Cache-Control", ""))
        self.assertNotIn("Cookie", response.get("Vary", "") or "")
        self.assertNotIn("sessionid", response.cookies)
        self.assertNotIn(b"wagtail-userbar", response.content)

    def test_authenticated_staff_response_is_never_shared(self):
        """
        A staff member browsing the live front end (not admin preview) must
        never have their response - wagtailuserbar included - handed to the
        shared public cache.
        """
        staff_user = User.objects.create_user(
            username="editor",
            password="password",  # noqa: S106
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(staff_user)

        response = self.client.get(
            self.test_page.url, headers={"user-agent": "Mozilla/5.0"}
        )

        self.assertIn("Cookie", response.get("Vary", ""))
        self.assertIn("sessionid", response.cookies)
        self.assertIn(b"wagtail-userbar", response.content)
