from django.conf import settings


class PublicCacheVaryCookieMiddleware:
    """Stop personalisation session access from defeating CDN caching.

    wagtail-personalisation's ``before_serve_page`` hooks (``set_visit_count``,
    ``segment_user``) read and write ``request.session`` on every page view,
    regardless of whether any personalised content ends up being shown, so
    that rules such as ``UserTypeRule`` can track returning visitors. The
    moment a session is touched, Django's ``SessionMiddleware`` adds
    ``Vary: Cookie`` to the response and issues a fresh ``sessionid`` cookie
    for new visitors.

    Because every anonymous visitor's session cookie is unique, ``Vary:
    Cookie`` means Cloudflare can never produce a cache hit for any page -
    including ones that ``rca.utils.models.BasePage.serve`` has already
    decided are safe to cache publicly when no personalised CTA matched
    (see ``_has_personalised_ctas``).

    This middleware restores that intent: for a response the view has
    already marked ``Cache-Control: public`` (and not ``no-store``), it
    drops the ``Cookie`` vary dimension and the session cookie that
    triggered it, so the CDN can actually cache the response. Responses
    carrying personalised content are left untouched, since they're already
    correctly marked as never cacheable.

    Must sit immediately above ``SessionMiddleware`` in ``MIDDLEWARE`` so
    this runs *after* ``SessionMiddleware``'s own response handling (Django
    runs middleware response handling in reverse of ``MIDDLEWARE`` order).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        cache_control = response.get("Cache-Control", "")
        if "public" not in cache_control or "no-store" in cache_control:
            return response

        vary_values = [
            value.strip()
            for value in response.get("Vary", "").split(",")
            if value.strip() and value.strip().lower() != "cookie"
        ]
        if vary_values:
            response["Vary"] = ", ".join(vary_values)
        elif "Vary" in response:
            del response["Vary"]

        session_cookie_name = settings.SESSION_COOKIE_NAME
        if session_cookie_name in response.cookies:
            del response.cookies[session_cookie_name]

        return response
