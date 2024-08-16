from django.urls import re_path
from wagtail import hooks
from wagtail_modeladmin.helpers import PermissionHelper
from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register

from rca.scholarships.models import ScholarshipEnquiryFormSubmission
from rca.scholarships.views import scholarships_delete


class ScholarshipEnquiryFormSubmissionPermissionHelper(PermissionHelper):
    def user_can_create(self, user):
        return False


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
        "programme",
        "scholarships",
        "eligibility",
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

    def scholarships(self, submission):
        return "|".join([s.title for s in submission.get_scholarships()])

    def eligibility(self, submission):
        return "|".join([s.title for s in submission.eligibility_criteria.all()])


class ScholarshipAdminGroup(ModelAdminGroup):
    menu_label = "Scholarships"
    menu_icon = "folder-open-inverse"
    menu_order = 200
    items = (ScholarshipEnquiryFormSubmissionAdmin,)


modeladmin_register(ScholarshipAdminGroup)


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        re_path(
            r"^scholarships/delete",
            scholarships_delete,
            name="scholarships_delete",
        ),
    ]
