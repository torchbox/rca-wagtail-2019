from django.urls import path

from .views import load_scholarships

app_name = "scholarships"

urlpatterns = [
    path(
        "ajax/load-scholarships/",
        load_scholarships,
        name="ajax_load_scholarships",
    ),
]
