from django.urls import path

from .views import (
    ScholarshipEnquiryFormThanksView,
    ScholarshipEnquiryFormView,
    load_scholarships,
)

app_name = "scholarships"

urlpatterns = [
    path(
        "",
        ScholarshipEnquiryFormView.as_view(),
        name="scholarship_enquiry_form",
    ),
    path(
        "thanks/",
        ScholarshipEnquiryFormThanksView.as_view(),
        name="scholarship_enquiry_form_thanks",
    ),
    path(
        "ajax/load-scholarships/",
        load_scholarships,
        name="ajax_load_scholarships",
    ),
]
