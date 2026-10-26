from wagtail_personalisation.adapters import SessionSegmentsAdapter


class RequestSegmentsAdapter(SessionSegmentsAdapter):
    """Evaluate segments once per request and retain editor overrides."""

    def __init__(self, request):
        super().__init__(request)
        self._refreshed = False

    def refresh(self):
        if self._refreshed:
            return

        super().refresh()
        self._refreshed = True
