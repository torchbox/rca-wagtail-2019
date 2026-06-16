from django.urls import re_path
from wagtail import hooks

from .views import delete as enquire_to_study_delete
from .viewsets import EnquiryFormSubmissionViewSet


@hooks.register("register_admin_viewset")
def register_enquiry_form_submission_viewset():
    return EnquiryFormSubmissionViewSet()


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        re_path(
            r"^enquire_to_study/delete",
            enquire_to_study_delete,
            name="enquiretostudy_delete",
        ),
    ]
