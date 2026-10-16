from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings

from rca.personalisation.middleware import PublicCacheVaryCookieMiddleware


class PublicCacheVaryCookieMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def get_response_through_middleware(self, response):
        middleware = PublicCacheVaryCookieMiddleware(
            get_response=lambda request: response
        )
        request = self.factory.get("/")
        return middleware(request)

    def test_strips_cookie_vary_from_public_response(self):
        response = HttpResponse()
        response["Cache-Control"] = "public, s-maxage=600"
        response["Vary"] = "Cookie, Origin"
        response.set_cookie("sessionid", "abc123")

        result = self.get_response_through_middleware(response)

        self.assertEqual(result["Vary"], "Origin")
        self.assertNotIn("sessionid", result.cookies)

    def test_removes_vary_header_entirely_if_only_cookie_was_set(self):
        response = HttpResponse()
        response["Cache-Control"] = "public, s-maxage=600"
        response["Vary"] = "Cookie"
        response.set_cookie("sessionid", "abc123")

        result = self.get_response_through_middleware(response)

        self.assertNotIn("Vary", result)
        self.assertNotIn("sessionid", result.cookies)

    def test_leaves_never_cached_response_untouched(self):
        response = HttpResponse()
        response["Cache-Control"] = (
            "max-age=0, no-cache, no-store, must-revalidate, private"
        )
        response["Vary"] = "Cookie, Origin"
        response.set_cookie("sessionid", "abc123")

        result = self.get_response_through_middleware(response)

        self.assertEqual(result["Vary"], "Cookie, Origin")
        self.assertIn("sessionid", result.cookies)
        self.assertEqual(result.cookies["sessionid"].value, "abc123")

    def test_leaves_response_without_cache_control_untouched(self):
        response = HttpResponse()
        response["Vary"] = "Cookie"
        response.set_cookie("sessionid", "abc123")

        result = self.get_response_through_middleware(response)

        self.assertEqual(result["Vary"], "Cookie")
        self.assertIn("sessionid", result.cookies)

    @override_settings(SESSION_COOKIE_NAME="custom_session")
    def test_uses_configured_session_cookie_name(self):
        response = HttpResponse()
        response["Cache-Control"] = "public, s-maxage=600"
        response["Vary"] = "Cookie"
        response.set_cookie("custom_session", "abc123")

        result = self.get_response_through_middleware(response)

        self.assertNotIn("custom_session", result.cookies)
