from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from rca.personalisation.middleware import (
    PublicCacheVaryCookieMiddleware,
    _strip_cookie_vary_dimension,
)
from rca.utils.cache import mark_response_cdn_cache_safe

User = get_user_model()


class StripCookieVaryDimensionTest(TestCase):
    def test_no_vary_header_is_a_no_op(self):
        response = HttpResponse()

        _strip_cookie_vary_dimension(response)

        self.assertNotIn("Vary", response)

    def test_removes_vary_header_entirely_when_cookie_is_the_only_dimension(self):
        response = HttpResponse()
        response["Vary"] = "Cookie"

        _strip_cookie_vary_dimension(response)

        self.assertNotIn("Vary", response)

    def test_matches_cookie_case_insensitively(self):
        response = HttpResponse()
        response["Vary"] = "cookie"

        _strip_cookie_vary_dimension(response)

        self.assertNotIn("Vary", response)

    def test_keeps_other_dimensions_and_drops_only_cookie(self):
        response = HttpResponse()
        response["Vary"] = "Cookie, Accept-Encoding"

        _strip_cookie_vary_dimension(response)

        self.assertEqual(response["Vary"], "Accept-Encoding")

    def test_leaves_dimensions_untouched_when_cookie_is_absent(self):
        response = HttpResponse()
        response["Vary"] = "Accept-Encoding"

        _strip_cookie_vary_dimension(response)

        self.assertEqual(response["Vary"], "Accept-Encoding")


class PublicCacheVaryCookieMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def build_response(
        self,
        cache_control,
        vary=None,
        with_session_cookie=True,
        extra_cookies=None,
        user=None,
        marked=True,
    ):
        def get_response(request):
            response = HttpResponse()
            response["Cache-Control"] = cache_control
            if vary is not None:
                response["Vary"] = vary
            if with_session_cookie:
                response.set_cookie(settings.SESSION_COOKIE_NAME, "abc123")
            for name, value in (extra_cookies or {}).items():
                response.set_cookie(name, value)
            if marked:
                mark_response_cdn_cache_safe(response)
            return response

        middleware = PublicCacheVaryCookieMiddleware(get_response)
        request = self.factory.get("/")
        if user is not None:
            request.user = user
        return middleware(request)

    def test_strips_session_cookie_from_public_response(self):
        response = self.build_response(cache_control="max-age=600, public")

        self.assertNotIn(settings.SESSION_COOKIE_NAME, response.cookies)

    def test_strips_cookie_vary_dimension_from_public_response(self):
        response = self.build_response(
            cache_control="max-age=600, public", vary="Cookie, Accept-Encoding"
        )

        self.assertEqual(response["Vary"], "Accept-Encoding")

    def test_removes_vary_header_entirely_when_cookie_was_only_dimension(self):
        response = self.build_response(
            cache_control="max-age=600, public", vary="Cookie"
        )

        self.assertNotIn("Vary", response)

    def test_leaves_private_response_untouched(self):
        response = self.build_response(
            cache_control="max-age=0, no-cache, no-store, must-revalidate, private",
            vary="Cookie",
        )

        self.assertIn(settings.SESSION_COOKIE_NAME, response.cookies)
        self.assertEqual(response["Vary"], "Cookie")

    def test_leaves_response_with_no_cache_control_untouched(self):
        response = self.build_response(cache_control="")

        self.assertIn(settings.SESSION_COOKIE_NAME, response.cookies)

    def test_leaves_unrelated_vary_dimensions_on_private_response_untouched(self):
        response = self.build_response(
            cache_control="private", vary="Cookie, Accept-Encoding"
        )

        self.assertEqual(response["Vary"], "Cookie, Accept-Encoding")

    def test_leaves_cookie_vary_dimension_when_other_cookies_are_set(self):
        """
        A ``csrftoken`` cookie (set by CsrfViewMiddleware when a template
        renders ``{% csrf_token %}``) means the response genuinely varies
        per visitor. Stripping "Cookie" from Vary in that case would let the
        CDN cache and replay one visitor's CSRF secret to everyone else.
        """
        response = self.build_response(
            cache_control="max-age=600, public",
            vary="Cookie, Accept-Encoding",
            extra_cookies={"csrftoken": "unique-secret"},
        )

        self.assertEqual(response["Vary"], "Cookie, Accept-Encoding")
        self.assertIn("csrftoken", response.cookies)

    def test_leaves_session_cookie_when_other_cookies_are_set(self):
        """
        When another cookie (e.g. csrftoken) means the response can't be
        shared anyway, there's no caching benefit to stripping the session
        cookie too - so it's left alone rather than silently discarded for
        nothing.
        """
        response = self.build_response(
            cache_control="max-age=600, public",
            vary="Cookie",
            extra_cookies={"csrftoken": "unique-secret"},
        )

        self.assertIn(settings.SESSION_COOKIE_NAME, response.cookies)
        self.assertIn("csrftoken", response.cookies)
        self.assertEqual(response["Vary"], "Cookie")

    def test_strips_session_cookie_when_it_is_the_only_cookie_present(self):
        response = self.build_response(
            cache_control="max-age=600, public", vary="Cookie"
        )

        self.assertNotIn(settings.SESSION_COOKIE_NAME, response.cookies)
        self.assertNotIn("Vary", response)

    def test_leaves_response_with_no_session_cookie_untouched(self):
        """
        A public, marked, cookie-free response (e.g. a repeat visitor who
        already has a matching csrftoken cookie, so Django didn't need to
        re-send one) should still have its Vary dimension stripped even
        though there was never a session cookie to delete.
        """
        response = self.build_response(
            cache_control="max-age=600, public",
            vary="Cookie",
            with_session_cookie=False,
        )

        self.assertNotIn(settings.SESSION_COOKIE_NAME, response.cookies)
        self.assertNotIn("Vary", response)

    def test_leaves_response_marked_both_public_and_private_untouched(self):
        response = self.build_response(
            cache_control="max-age=600, public, private", vary="Cookie"
        )

        self.assertIn(settings.SESSION_COOKIE_NAME, response.cookies)
        self.assertEqual(response["Vary"], "Cookie")

    def test_leaves_authenticated_user_response_untouched(self):
        """
        {% wagtailuserbar %} renders real edit-the-page markup for any user
        with admin access, regardless of the page. A staff member's response
        must never be handed to the shared public cache, even when it would
        otherwise qualify (public Cache-Control, no other cookies set).
        """
        staff_user = User(username="editor", is_staff=True)

        response = self.build_response(
            cache_control="max-age=600, public",
            vary="Cookie",
            user=staff_user,
        )

        self.assertIn(settings.SESSION_COOKIE_NAME, response.cookies)
        self.assertEqual(response["Vary"], "Cookie")

    def test_strips_anonymous_user_response(self):
        response = self.build_response(
            cache_control="max-age=600, public",
            vary="Cookie",
            user=AnonymousUser(),
        )

        self.assertNotIn(settings.SESSION_COOKIE_NAME, response.cookies)
        self.assertNotIn("Vary", response)

    def test_leaves_unmarked_public_response_untouched(self):
        """
        ``Cache-Control: public`` alone is not enough evidence a response is
        free of per-visitor data. Only responses explicitly opted in via
        ``mark_response_cdn_cache_safe`` (called from ``Page.serve()`` and
        the search view, which know *why* a stray session cookie/Vary would
        appear) are touched - any other code path that happens to mark a
        response public (e.g. the generic cache_control decorator applied to
        sitemap.xml/social-auth URLs in urls.py) is left alone.
        """
        response = self.build_response(
            cache_control="max-age=600, public", vary="Cookie", marked=False
        )

        self.assertIn(settings.SESSION_COOKIE_NAME, response.cookies)
        self.assertEqual(response["Vary"], "Cookie")
