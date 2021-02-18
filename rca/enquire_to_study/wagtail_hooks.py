from wagtail.contrib.modeladmin.helpers import PermissionHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from rca.enquire_to_study.models import EnquiryFormSubmission


class EnquiryFormSubmissionPermissionHelper(PermissionHelper):
    def user_can_list(self, user):
        return True

    def user_can_create(self, user):
        return False

    def user_can_edit_obj(self, user, obj):
        return True

    def user_can_delete_obj(self, user, obj):
        return True


class EnquiryFormSubmissionAdmin(ModelAdmin):
    model = EnquiryFormSubmission
    menu_label = "Enquiry Submissions"
    menu_icon = "doc-full"
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
    permission_helper_class = EnquiryFormSubmissionPermissionHelper


modeladmin_register(EnquiryFormSubmissionAdmin)
