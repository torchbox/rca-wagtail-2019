from django.contrib.contenttypes.models import ContentType
from import_export import resources
from import_export.admin import ImportMixin
from wagtail.models import Page

from .page_import_forms import PageConfirmImportForm, PageImportForm


class PageImportMixin(ImportMixin):
    import_template_name = "admin/import_export/page_import.html"

    def get_import_form(self):
        return PageImportForm

    def get_confirm_import_form(self):
        return PageConfirmImportForm

    def import_action(self, request, *args, **kwargs):
        self.request = request
        return super().import_action(request, *args, **kwargs)

    def get_import_resource_kwargs(self, request, *args, **kwargs):
        init_kwargs = super().get_import_resource_kwargs(request, *args, **kwargs)
        form_data = getattr(kwargs["form"], "cleaned_data", {})
        init_kwargs["request"] = request
        init_kwargs["parent_page"] = form_data.get("parent_page")
        init_kwargs["owner"] = form_data.get("owner")
        return init_kwargs

    def get_parent_page_queryset(self):
        allowed_content_types = list(
            ContentType.objects.get_for_models(
                *self.model.allowed_parent_page_models()
            ).values()
        )
        return Page.objects.filter(content_type__in=allowed_content_types, depth__gt=1)

    def get_form_kwargs(self, form, *args, **kwargs):
        vals = super().get_form_kwargs(form, *args, **kwargs)
        if isinstance(form, PageImportForm):
            # The method is just being used to prep the 'initial data' for the
            # 'confirm' form, so pass through the values from the 'import' form.
            vals.update(
                parent_page=form.cleaned_data["parent_page"],
                owner=form.cleaned_data["owner"],
            )
            return vals

        # The method is being used to prepare full 'init' values for the 'import'
        # form. So, add additional required values, as well as adding some helpful
        # initial data values
        parent_page_queryset = self.get_parent_page_queryset()
        vals.update(
            admin_site=self.admin_site, parent_page_queryset=parent_page_queryset
        )
        initial_vals = vals.get("initial", {})
        initial_vals["parent_page"] = parent_page_queryset.first()
        initial_vals["owner"] = self.request.user.id
        vals["initial"] = initial_vals
        return vals


class PageResource(resources.ModelResource):
    def __init__(self, request, parent_page, owner, **kwargs):
        """
        Overrides ModelResource.__init__() to accept the required
        'request', 'parent_page' and 'owner' arguments. Which are
        used to create new pages and revisions.
        """
        self.parent_page = parent_page
        self.request = request
        self.owner = owner
        super().__init__(**kwargs)

    def after_import_row(self, row, row_result, **kwargs):
        """
        If diffing is disabled (required for pages, due to a pickling issue),
        Add a 'fake' diff to the row_result, so that row values are shown
        in the template (otherwise it looks like all rows are blank).
        """
        if row_result.diff is None:
            row_result.diff = [row.get(h, "") for h in self.get_diff_headers()]

    def save_instance(self, instance, using_transactions=True, dry_run=False):
        """
        Saves the page to the database
        """
        self.before_save_instance(instance, using_transactions, dry_run)
        if not dry_run:
            if instance._state.adding:
                # Set owner
                instance.owner = self.owner
                # Keep page as draft
                instance.live = False
                # Save the new page
                self.parent_page.add_child(instance=instance)
            else:
                # Update existing
                instance.save()
        self.after_save_instance(instance, using_transactions, dry_run)

    def after_save_instance(self, instance, using_transactions=True, dry_run=False):
        """
        Overrides ImportMixin.after_save_instance() to create a new page
        revision after saving the page itself.
        """
        super().after_save_instance(instance, using_transactions, dry_run)
        if not dry_run:
            instance.save_revision(user=self.request.user)
