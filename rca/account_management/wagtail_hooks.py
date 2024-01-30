from django.conf import settings
from django.shortcuts import reverse
from django.urls import re_path
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from .views import CreateStudentFormView

WAGTAIL_FRONTEND_LOGIN_TEMPLATE = getattr(
    settings, "WAGTAIL_FRONTEND_LOGIN_TEMPLATE", "wagtailcore/login.html"
)


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        re_path(
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
        order=10000,
        icon_name="user",
    )


@hooks.register("construct_main_menu")
def hide_explorer_menu_item_from_students(request, menu_items):
    if request.user.is_student():
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


@hooks.register("construct_homepage_panels")
def strip_homepage_panels_for_students(request, panels):
    if request.user.is_student():
        for i, v in enumerate(panels):
            del panels[i]
    return panels
