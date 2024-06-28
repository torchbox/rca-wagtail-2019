from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.permissions import page_permission_policy

from .views import AgingPagesReportView


@hooks.register("register_admin_urls")
def register_custom_aging_pages_report():
    return [
        path(
            "reports/rca-aging-pages/",
            AgingPagesReportView.as_view(),
            name="rca_aging_pages_report",
        ),
    ]


class AgingPagesReportMenuItem(MenuItem):
    def is_shown(self, request):
        return page_permission_policy.user_has_any_permission(
            request.user, ["add", "change", "publish"]
        )


@hooks.register("register_reports_menu_item")
def register_aging_pages_report_menu_item():
    return AgingPagesReportMenuItem(
        "Aging pages",
        reverse("rca_aging_pages_report"),
        name="aging-pages",
        icon_name="time",
        order=1100,
    )
