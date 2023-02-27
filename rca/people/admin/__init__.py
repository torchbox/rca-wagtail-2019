from django.contrib import admin
from import_export import widgets
from import_export.fields import Field
from wagtail.models import Page

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
        # If not set, diffing pages triggers 'pickle' errors
        skip_diff = True
        # Pages clean themselves automatically on save()
        clean_model_instances = False
        import_id_fields = ("legacy_staff_id",)
        fields = (
            "legacy_staff_id",
            "title",
            "slug",
            "staff_title",
            "first_name",
            "last_name",
        )

    def before_save_instance(self, instance, using_transactions=True, dry_run=False):
        """
        Add missing required field values.
        """
        if not instance.title:
            instance.title = instance.name


@admin.register(StaffPage)
class StaffPageModelAdmin(PageImportMixin, admin.ModelAdmin):
    list_display = ("staff_title", "first_name", "last_name", "live")
    resource_class = StaffPageResource


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "live")
    search_fields = ("title", "slug")
