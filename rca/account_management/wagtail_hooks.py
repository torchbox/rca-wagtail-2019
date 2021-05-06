from django.conf import settings
from django.conf.urls import url
from django.shortcuts import reverse
from wagtail.admin.menu import MenuItem
from wagtail.core import hooks

from .views import CreateStudentFormView

WAGTAIL_FRONTEND_LOGIN_TEMPLATE = getattr(
    settings, "WAGTAIL_FRONTEND_LOGIN_TEMPLATE", "wagtailcore/login.html"
)


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        url(
            r"^student/create",
            CreateStudentFormView.as_view(),
            name="student_account_create",
        ),
    ]


@hooks.register("register_admin_menu_item")
def register_student_menu_item():
    return MenuItem(
        "Student accounts",
        reverse("student_account_create"),
        classnames="icon icon-user",
        order=10000,
    )
