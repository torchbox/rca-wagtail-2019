from django.conf.urls import url
from wagtail import hooks
from wagtail.contrib.modeladmin.helpers import PermissionHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail_rangefilter.filters import DateTimeRangeFilter

from rca.enquire_to_study.models import EnquiryFormSubmission

from .views import delete as enquire_to_study_delete


class EnquiryFormSubmissionPermissionHelper(PermissionHelper):
    def user_can_list(self, user):
        return user.is_superuser

    def user_can_create(self, user):
        return False

    def user_can_edit_obj(self, user, obj):
        return user.is_superuser

    def user_can_delete_obj(self, user, obj):
        return user.is_superuser


class EnquiryFormSubmissionAdmin(ModelAdmin):
    model = EnquiryFormSubmission
    menu_label = "Enquiry Submissions"
    menu_icon = "doc-full"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    index_template_name = "enquire_to_study/index.html"
    list_export = (
        "submission_date",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "get_country_of_residence",
        "city",
        "country_of_citizenship",
        "enquiry_reason",
        "start_date",
        "is_read_data_protection_policy",
        "is_notification_opt_in",
        "get_programmes",
    )
    list_display = (
        "submission_date",
        "first_name",
        "last_name",
        "email",
        "country_of_citizenship",
        "start_date",
        "get_programmes",
    )

    def get_programmes(self, obj):
        return ", ".join(
            str(item.programme.title)
            for item in obj.enquiry_submission_programmes.all()
        )

    get_programmes.short_description = "Programmes"

    def get_country_of_residence(self, obj):
        return obj.country_of_residence.name

    get_country_of_residence.short_description = "Country of residence"

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.select_related(
            "enquiry_reason",
            "start_date",
        ).prefetch_related("enquiry_submission_programmes__programme")

    list_filter = (
        ("submission_date", DateTimeRangeFilter),
        "enquiry_submission_programmes__programme",
    )

    search_fields = ("first_name", "last_name", "email", "country_of_residence")
    permission_helper_class = EnquiryFormSubmissionPermissionHelper


modeladmin_register(EnquiryFormSubmissionAdmin)


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        url(
            r"^enquire_to_study/delete",
            enquire_to_study_delete,
            name="enquiretostudy_delete",
        ),
    ]
