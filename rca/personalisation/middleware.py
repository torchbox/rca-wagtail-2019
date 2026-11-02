from django.conf import settings
from django.utils.cache import add_never_cache_headers

from .cache import (
    ANONYMOUS_CACHE_COOKIE,
    SHARED_PAGE_HEADER,
    SHARED_PAGE_VERSION,
    set_anonymous_cache_cookie,
)


class AnonymousCacheMiddleware:
    """Issue edge-cache markers after SessionMiddleware saves the session.

    This must precede SessionMiddleware in MIDDLEWARE so response processing sees
    the final session key, including the new key produced by Django login.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            len(settings.PERSONALISATION_CACHE_SIGNING_KEY.encode()) < 32
            or request.get_host().lower() != settings.PERSONALISATION_CACHE_HOSTNAME
            or not request.is_secure()
        ):
            return response

        user = getattr(request, "user", None)
        if user is None:
            return response
        if user.is_authenticated:
            if request.COOKIES.get(ANONYMOUS_CACHE_COOKIE):
                response.delete_cookie(ANONYMOUS_CACHE_COOKIE, path="/", samesite="Lax")
            add_never_cache_headers(response)
            return response

        if response.status_code != 200:
            return response
        if getattr(request, "_anonymous_cache_marker_eligible", False):
            set_anonymous_cache_cookie(request, response)
            add_never_cache_headers(response)
        elif getattr(request, "_defer_personalisation", False):
            response[SHARED_PAGE_HEADER] = SHARED_PAGE_VERSION
        return response
