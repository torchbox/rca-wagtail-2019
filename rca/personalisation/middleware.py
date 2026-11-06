from .restrictions import cache_page_view_restrictions


class AnonymousCacheMiddleware:
    """Cache page restriction lookups for the duration of each request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        with cache_page_view_restrictions(request):
            return self.get_response(request)
