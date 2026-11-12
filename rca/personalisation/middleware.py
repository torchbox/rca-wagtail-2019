from django.conf import settings

from rca.utils.cache import CDN_CACHE_SAFE_ATTR


def _strip_cookie_vary_dimension(response):
    """
    Remove "Cookie" from the response's ``Vary`` header in place, leaving
    any other dimensions (e.g. ``Accept-Encoding``) untouched.
    """
    vary = response.get("Vary")
    if not vary:
        return

    remaining_dimensions = [
        dimension
        for dimension in (v.strip() for v in vary.split(","))
        if dimension.lower() != "cookie"
    ]
    if remaining_dimensions:
        response["Vary"] = ", ".join(remaining_dimensions)
    else:
        del response["Vary"]


class PublicCacheVaryCookieMiddleware:
    """
    wagtail-personalisation touches ``request.session`` on every page view,
    which makes Django add a session cookie and ``Vary: Cookie`` to every
    response - even ones a page's own ``serve()`` has marked
    ``Cache-Control: public`` because no personalised content applies. The
    CDN in front of this site treats any response carrying a session cookie
    as private, regardless of Cache-Control, so that cookie and vary
    dimension are stripped here to let such responses be cached.

    Only responses explicitly opted in via
    ``rca.utils.cache.mark_response_cdn_cache_safe`` are touched -
    ``Cache-Control: public`` alone isn't evidence a response is free of
    other per-visitor data, so stripping is scoped to call sites
    (``Page.serve()``, the search view) that know why a stray session
    cookie/Vary would appear on their response.

    Left untouched: responses with another cookie set (e.g. CsrfViewMiddleware's
    per-visitor ``csrftoken`` on a form page) - dropping ``Vary: Cookie`` there
    would let the CDN replay one visitor's CSRF secret to everyone; and
    authenticated requests - {% wagtailuserbar %} renders real edit-the-page
    markup for any admin user, so staff responses must never hit the shared
    public cache.

    Leaving another cookie in place is enough on its own to keep a response
    out of the shared cache, independently of whether ``Vary``/``Cache-Control``
    get stripped here:

    - Django's ``get_token()`` re-sends the ``csrftoken`` cookie on *every*
      render of ``{% csrf_token %}``, even for a visitor who already has a
      valid one (it renews the cookie's expiry) - so a CSRF-rendering page's
      response always carries that cookie, not just on a visitor's first
      visit.
    - The production Cloudflare Worker's Cache API never stores a response
      that carries a ``Set-Cookie`` header at all, regardless of
      ``Cache-Control``/``Vary``. See ``infrastructure/cloudflare/caching-worker.mjs``.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not getattr(response, CDN_CACHE_SAFE_ATTR, False):
            return response

        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            return response

        cache_control = response.get("Cache-Control", "")
        if "public" not in cache_control or "private" in cache_control:
            return response

        session_cookie_name = settings.SESSION_COOKIE_NAME
        other_cookies_present = any(
            name != session_cookie_name for name in response.cookies
        )
        if other_cookies_present:
            return response

        # NOTE: dropping the session cookie re-rolls a repeat visitor's
        # assignment on every public view for any Segment using
        # `randomisation_percent` (none currently - a CMS-content fact, not
        # visible from code). Check for active randomised segments before
        # relying on this middleware if that changes.
        if session_cookie_name in response.cookies:
            del response.cookies[session_cookie_name]

        _strip_cookie_vary_dimension(response)

        return response
