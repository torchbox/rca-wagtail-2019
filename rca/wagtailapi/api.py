from wagtail.api.v2 import router

from rca.wagtailapi.endpoints import SitewideAlertEndpoint
from rca.wagtailapi.views import NavigationAPIViewSet, PagesAPIViewSet

api_router = router.WagtailAPIRouter("wagtailapi")
api_router.register_endpoint("pages", PagesAPIViewSet)
api_router.register_endpoint("navigation", NavigationAPIViewSet)
api_router.register_endpoint("sitewide-alert", SitewideAlertEndpoint)
