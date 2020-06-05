from django.contrib import admin
from import_export import widgets
from import_export.fields import Field
from wagtail.core.models import Page

from ..models import StaffPage
from .page_import import PageImportMixin, PageResource


class StaffPageResource(PageResource):
    legacy_staff_id = Field(
        attribute="legacy_staff_id",
        column_name="id",
        default=None,
        widget=widgets.IntegerWidget(),
    )
    staff_title = Field(
        attribute="staff_title",
        column_name="title_prefix",
        default="",
        widget=widgets.CharWidget(),
    )

    class Meta:
        model = StaffPage
        skip_diff = True
        use_transactions = True
        import_id_fields = ("legacy_staff_id",)
        fields = (
            "legacy_staff_id",
            "slug",
            "staff_title",
            "first_name",
            "last_name",
            "job_title",
        )

    def before_save_instance(self, instance, using_transactions, dry_run):
        if not instance.title:
            instance.title = instance.name
        if not instance.job_title:
            instance.job_title = "TBC"


@admin.register(StaffPage)
class StaffPageModelAdmin(PageImportMixin, admin.ModelAdmin):
    list_display = ("name", "job_title", "live")
    resource_class = StaffPageResource


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "live")
    search_fields = ("title", "slug")
