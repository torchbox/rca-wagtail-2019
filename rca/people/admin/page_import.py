from import_export import resources
from import_export.admin import ImportMixin

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

    def get_form_kwargs(self, form, *args, **kwargs):
        form_kwargs = super().get_form_kwargs(form, *args, **kwargs)
        form_kwargs.update(admin_site=self.admin_site, page_type=self.model)
        if isinstance(form, PageImportForm):
            initial_vals = form_kwargs.get("initial", {})
            initial_vals["owner"] = self.request.user.id
            form_kwargs["initial"] = initial_vals
        return form_kwargs


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

    def save_instance(self, instance, using_transactions=True, dry_run=False):
        """
        Takes care of saving the page to the database.
        Keep in mind that this is done by calling ``instance.save()``, so
        objects are not created in bulk!
        """
        self.before_save_instance(instance, using_transactions, dry_run)
        if not dry_run or using_transactions:
            if instance._state.adding:
                # Add page to tree with the owner value set
                instance.owner = self.owner
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
        if not dry_run or using_transactions:
            instance.save_revision(user=self.request.user)
