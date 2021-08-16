from django.urls import path

from rca.enquire_to_study.views import (
    EnquireToStudyFormThanksView,
    EnquireToStudyFormView,
)

app_name = "enquire_to_study"

urlpatterns = [
    path("", EnquireToStudyFormView.as_view(), name="enquire_to_study_form"),
    path(
        "thanks/",
        EnquireToStudyFormThanksView.as_view(),
        name="enquire_to_study_thanks",
    ),
]
