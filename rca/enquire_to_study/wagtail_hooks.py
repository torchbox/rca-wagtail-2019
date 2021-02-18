from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from rca.enquire_to_study.models import Submission


class SubmissionAdmin(ModelAdmin):
    model = Submission
    menu_label = "Submission"
    menu_icon = "pick"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = (
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "country_of_residence",
    )
    list_filter = ("country_of_residence",)
    search_fields = ("first_name", "last_name", "email", "country_of_residence")


modeladmin_register(SubmissionAdmin)
