from django import forms
from django.contrib.admin.widgets import AutocompleteSelect
from django.contrib.auth import get_user_model
from import_export.forms import ConfirmImportForm, ImportForm
from wagtail.models import Page

User = get_user_model()


class PageImportFormMixin(forms.Form):
    owner = forms.ModelChoiceField(
        label="Owner (for new pages)", queryset=User.objects.all()
    )
    parent_page = forms.ModelChoiceField(
        label="Add new pages below", queryset=Page.objects.all()
    )


class PageImportForm(PageImportFormMixin, ImportForm):
    autocomplete_fields = ["owner", "parent_page"]

    def __init__(self, *args, admin_site, parent_page_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Set 'parent_page' queryset to the provided one
        if parent_page_queryset is not None:
            self.fields["parent_page"].queryset = parent_page_queryset

        # Replace standard modelchoice select widgets with
        # AutocompleteSelect - which is much more efficient
        # when the queryset is potentially quite large
        for field_name in self.autocomplete_fields:
            field = self.fields[field_name]
            field.widget = AutocompleteSelect(
                field.queryset,
                admin_site,
                using=field.queryset.db,
                choices=field.widget.choices,
            )


class PageConfirmImportForm(PageImportFormMixin, ConfirmImportForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide new owner and parent_page fields
        for field_name in ("owner", "parent_page"):
            self.fields[field_name].widget = forms.HiddenInput()
