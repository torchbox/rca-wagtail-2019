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


@hooks.register("construct_main_menu")
def hide_explorer_menu_item_from_frank(request, menu_items):
    if request.user.groups.filter(name="Students").exists():
        # Hide menu items for students
        items_to_hide = [
            "reports",
            "explorer",
            "forms",
            "taxonomies",
            "student-accounts",
            "settings",
            "images",
        ]
        menu_items[:] = [item for item in menu_items if item.name not in items_to_hide]
