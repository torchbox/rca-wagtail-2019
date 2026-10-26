from wagtail_personalisation.adapters import SessionSegmentsAdapter


class RequestSegmentsAdapter(SessionSegmentsAdapter):
    """Evaluate segments once per request and retain editor overrides."""

    def __init__(self, request):
        self._deferred = getattr(request, "_defer_personalisation", False)
        self._refreshed = self._deferred
        if self._deferred:
            # The session adapter's initializer creates session state eagerly.
            self.request = request
        else:
            super().__init__(request)

    def add_page_visit(self, page):
        if not self._deferred:
            super().add_page_visit(page)

    def get_segments(self, key="segments"):
        if self._deferred:
            return []
        return super().get_segments(key)

    def refresh(self):
        if self._refreshed:
            return

        super().refresh()
        self._refreshed = True
