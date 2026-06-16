import django_filters
from django.urls import re_path, reverse
from wagtail import hooks
from wagtail.admin.filters import DateRangePickerWidget, WagtailFilterSet
from wagtail.admin.views.generic.models import IndexView
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.admin.widgets.button import HeaderButton
from wagtail.permission_policies import ModelPermissionPolicy

from rca.enquire_to_study.models import EnquiryFormSubmission
from rca.programmes.models import ProgrammePage

from .views import delete as enquire_to_study_delete


class DisableCreatePermissionPolicy(ModelPermissionPolicy):
    """Forbid creating new instances for every user (including superusers),
    reproducing the previous ``EnquiryFormSubmissionPermissionHelper`` whose
    ``user_can_create`` always returned ``False``. Enquiry submissions are only
    ever created by the public-facing form, never in the admin."""

    def user_has_permission(self, user, action):
        if action == "add":
            return False
        return super().user_has_permission(user, action)


class EnquiryFormSubmissionFilterSet(WagtailFilterSet):
    # ``submission_date`` was a wagtail-rangefilter ``DateTimeRangeFilter`` under
    # the django-admin-based modeladmin. Wagtail's viewset index uses django-filter,
    # so this is ported to django-filter's native date-range filter (the same
    # mechanism Wagtail core's own form-submissions listing uses).
    submission_date = django_filters.DateFromToRangeFilter(
        label="Submission date",
        widget=DateRangePickerWidget,
    )
    # Kept as a select dropdown (ModelChoiceFilter) to match the modeladmin
    # related-field filter widget.
    programme = django_filters.ModelChoiceFilter(
        field_name="enquiry_submission_programmes__programme",
        queryset=ProgrammePage.objects.all(),
        label="Programme",
    )

    class Meta:
        model = EnquiryFormSubmission
        fields = ["submission_date", "programme"]


class EnquiryFormSubmissionIndexView(IndexView):
    def get_base_queryset(self):
        return (
            super()
            .get_base_queryset()
            .select_related("enquiry_reason", "start_date")
            .prefetch_related("enquiry_submission_programmes__programme")
        )

    @property
    def header_buttons(self):
        buttons = super().header_buttons
        # Re-home the modeladmin index header action onto the viewset header.
        buttons.append(
            HeaderButton(
                "Delete submissions",
                url=reverse("enquiretostudy_delete"),
                icon_name="bin",
            )
        )
        return buttons


class EnquiryFormSubmissionViewSet(ModelViewSet):
    model = EnquiryFormSubmission
    index_view_class = EnquiryFormSubmissionIndexView
    icon = "doc-full"
    menu_label = "Enquiry Submissions"
    menu_order = 200
    add_to_admin_menu = True
    add_to_settings_menu = False
    # This is a read-only submission log: no create or copy in the admin.
    copy_view_enabled = False
    filterset_class = EnquiryFormSubmissionFilterSet
    search_fields = ("first_name", "last_name", "email", "country_of_residence")
    list_display = (
        "submission_date",
        "first_name",
        "last_name",
        "email",
        "country_of_citizenship",
        "start_date",
        "get_programmes",
    )
    list_export = (
        "submission_date",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "get_country_of_residence",
        "city",
        "get_country_of_citizenship",
        "enquiry_reason",
        "enquiry_questions",
        "start_date",
        "is_read_data_protection_policy",
        "is_notification_opt_in",
        "get_programmes",
    )

    @property
    def permission_policy(self):
        return DisableCreatePermissionPolicy(self.model)


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
