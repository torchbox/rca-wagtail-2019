from django.conf.urls import url
from wagtail.contrib.modeladmin.helpers import PermissionHelper
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from wagtail.core import hooks

from rca.scholarships.models import ScholarshipEnquiryFormSubmission
from rca.scholarships.views import scholarships_delete


class ScholarshipEnquiryFormSubmissionPermissionHelper(PermissionHelper):
    def user_can_list(self, user):
        return user.is_superuser

    def user_can_create(self, user):
        return False

    def user_can_edit_obj(self, user, obj):
        return user.is_superuser

    def user_can_delete_obj(self, user, obj):
        return user.is_superuser


class ScholarshipEnquiryFormSubmissionAdmin(ModelAdmin):
    model = ScholarshipEnquiryFormSubmission
    menu_label = "Scholarship Submissions"
    menu_icon = "doc-full"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    index_template_name = "scholarships/index.html"
    list_export = (
        "submission_date",
        "first_name",
        "last_name",
        "email",
        "rca_id_number",
        "is_read_data_protection_policy",
        "is_notification_opt_in",
    )
    list_display = (
        "submission_date",
        "first_name",
        "last_name",
        "email",
        "rca_id_number",
    )

    search_fields = ("first_name", "last_name", "email", "rca_id_number")
    permission_helper_class = ScholarshipEnquiryFormSubmissionPermissionHelper


class ScholarshipAdminGroup(ModelAdminGroup):
    menu_label = "Scholarships"
    menu_icon = "folder-open-inverse"
    menu_order = 200
    items = (ScholarshipEnquiryFormSubmissionAdmin,)


modeladmin_register(ScholarshipAdminGroup)


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        url(r"^scholarships/delete", scholarships_delete, name="scholarships_delete",),
    ]
