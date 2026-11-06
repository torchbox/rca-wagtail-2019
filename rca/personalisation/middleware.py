from django.utils.cache import add_never_cache_headers, has_vary_header
from wagtail.views import serve

from .cache import (
    ANONYMOUS_CACHE_COOKIE,
    SHARED_PAGE_HEADER,
    SHARED_PAGE_VERSION,
    is_anonymous_cache_enabled,
    set_anonymous_cache_cookie,
)
from .restrictions import cache_page_view_restrictions
from .state import get_personalisation_state


class AnonymousCacheMiddleware:
    """Issue edge-cache markers after SessionMiddleware saves the session.

    This must precede SessionMiddleware in MIDDLEWARE so response processing sees
    the final session key, including the new key produced by Django login.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        with cache_page_view_restrictions(request):
            response = self.get_response(request)
        return self._process_response(request, response)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if (
            view_func is not serve
            or request.method not in ("GET", "HEAD")
            or not is_anonymous_cache_enabled(request)
        ):
            return

        # Resolve Django's lazy user before rendering. Only this anonymous-user
        # lookup may be ignored: earlier and later session reads must still vary.
        session = request.session
        previously_accessed = session.accessed
        if not request.user.is_authenticated and not session.modified:
            session.accessed = previously_accessed

    def _process_response(self, request, response):
        if not is_anonymous_cache_enabled(request):
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

        state = get_personalisation_state(request)
        if state.anonymous_cache_marker_eligible:
            set_anonymous_cache_cookie(request, response)
            add_never_cache_headers(response)
        elif state.defer_personalisation:
            if has_vary_header(response, "Cookie") or response.cookies:
                response.headers.pop(SHARED_PAGE_HEADER, None)
                add_never_cache_headers(response)
            else:
                response[SHARED_PAGE_HEADER] = SHARED_PAGE_VERSION

        return response
