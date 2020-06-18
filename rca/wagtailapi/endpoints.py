from wagtail.api.v2 import endpoints

from rca.utils.models import SitewideAlertSetting


class SitewideAlertEndpoint(endpoints.BaseAPIEndpoint):
    model = SitewideAlertSetting
