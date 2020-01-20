from django.conf.urls import url
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from wagtail.admin.menu import MenuItem
from wagtail.core import hooks

from .views import ApiContentCacheClear, ApiContentCacheSettings


@hooks.register("register_admin_urls")
def urlconf_time():
    return [
        url(
            r"^api-cache/", ApiContentCacheSettings.as_view(), name="api-cache-settings"
        ),
        url(r"^api-cache/clear/", ApiContentCacheClear),
    ]


@hooks.register("register_settings_menu_item")
def register_api_content_settings_menu_item():
    return MenuItem(
        _("API content settings"),
        reverse("api-cache-settings"),
        classnames="icon icon-cog",
        order=1000,
    )
