from django import forms
from django.contrib.admin.widgets import AutocompleteSelect
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from import_export.forms import ConfirmImportForm, ImportForm
from wagtail.core.models import Page


class FakeRelation:
    def __init__(self, model):
        self.model = model


class PageImportFormMixin(forms.Form):
    owner = forms.ModelChoiceField(
        label="Owner (for new pages)", queryset=get_user_model().objects.all()
    )
    parent_page = forms.ModelChoiceField(
        label="Add new pages below", queryset=Page.objects.all()
    )

    def __init__(self, *args, **kwargs):
        self.admin_site = kwargs.pop("admin_site")
        self.page_type = kwargs.pop("page_type")
        super().__init__(*args, **kwargs)

        # Limit parent_page queryset according to page_type
        allowed_parent_page_content_types = list(
            ContentType.objects.get_for_models(
                *self.page_type.allowed_parent_page_models()
            ).values()
        )
        qs = Page.objects.filter(
            content_type__in=allowed_parent_page_content_types
        ).exclude(depth=1)
        self.fields["parent_page"].queryset = qs
        self.initial["parent_page"] = qs.first()


class PageImportForm(PageImportFormMixin, ImportForm):
    autocomplete_fields = ("owner", "parent_page")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Swap out standard select widgets for AutocompleteSelect
        for field_name in self.autocomplete_fields:
            field = self.fields[field_name]
            choices = field.widget.choices
            rel = FakeRelation(field.queryset.model)
            field.widget = AutocompleteSelect(
                rel,
                admin_site=self.admin_site,
                using=field.queryset.db,
                choices=choices,
            )


class PageConfirmImportForm(PageImportFormMixin, ConfirmImportForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide new owner and parent_page fields
        for field_name in ("owner", "parent_page"):
            self.fields[field_name].widget = forms.HiddenInput()
