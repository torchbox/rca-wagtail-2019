from django.conf.urls import url
from wagtail.core import hooks

from .views import ApiContentCacheClear, ApiContentCacheSettings


@hooks.register("register_admin_urls")
def urlconf_time():
    return [
        url(r"^api-cache/", ApiContentCacheSettings.as_view()),
        url(r"^api-cache/clear/", ApiContentCacheClear),
    ]
