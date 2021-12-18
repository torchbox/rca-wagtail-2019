from django.urls import path

from rca.scholarships.views import ScholarshipFormView, load_scholarships

app_name = "scholarships"

urlpatterns = [
    path("", ScholarshipFormView.as_view(), name="scholarship_enquiry"),
    path("ajax/load-scholarships/", load_scholarships, name="ajax_load_scholarships"),
]
