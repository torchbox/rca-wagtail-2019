from django.conf.urls import url
from wagtail.core import hooks

from .views import CreateStudentFormView


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        url(
            r"^student/create",
            CreateStudentFormView.as_view(),
            name="student_account_create",
        ),
    ]
