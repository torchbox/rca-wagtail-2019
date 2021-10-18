from wagtail.api.v2 import router

from rca.wagtailapi.views import (
    NavigationAPIViewSet,
    PagesAPIViewSet,
    RCAImagesViewset,
    SitewideAlertAPIViewSet,
)

api_router = router.WagtailAPIRouter("wagtailapi")
api_router.register_endpoint("pages", PagesAPIViewSet)
api_router.register_endpoint("navigation", NavigationAPIViewSet)
api_router.register_endpoint("sitewide-alert", SitewideAlertAPIViewSet)
api_router.register_endpoint("images", RCAImagesViewset)
