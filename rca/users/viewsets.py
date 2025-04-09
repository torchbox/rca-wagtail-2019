from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import Column, StatusTagColumn
from wagtail.users.views.users import IndexView
from wagtail.users.views.users import UserViewSet as WagtailUserViewSet

from rca.utils.columns import insert_columns

from .forms import CustomUserEditForm


class CustomUserIndexView(IndexView):
    """
    Extends UserIndexView to add admin status and group columns before the Status
    column.

    Reimplements customisation lost as part of the Wagtail 6.1 upgrade
    (90440d77dab70053be9cec69cb46a4f28b7da38c).
    """

    @cached_property
    def columns(self):
        columns = (
            StatusTagColumn(
                "is_superuser",
                accessor=lambda user: _("Yes") if user.is_superuser else _("No"),
                primary=lambda user: user.is_superuser,
                label=_("Admin"),
                sort_key="is_superuser",
            ),
            Column(
                "Groups",
                accessor=lambda user: ", ".join(
                    [group.name for group in user.groups.all()]
                ),
                label=_("Groups"),
            ),
        )

        return insert_columns(
            source_columns=super().columns,
            insert_before_column_ref="Status",
            columns_to_insert=columns,
        )


class UserViewSet(WagtailUserViewSet):
    index_view_class = CustomUserIndexView

    # This replaces the WAGTAIL_USER_EDIT_FORM
    def get_form_class(self, for_update=False):
        if for_update:
            return CustomUserEditForm
        return super().get_form_class(for_update)
