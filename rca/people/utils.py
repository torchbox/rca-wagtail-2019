from django.apps import apps
from django.db.models import Q
from wagtail.admin.edit_handlers import ObjectList, TabbedInterface
from wagtail.utils.decorators import cached_classmethod


def get_area_linked_filters(page):
    """For the expertise taxonomy thats listed out in key details,
    they need to link to the parent staff picker page with a filter pre
    selected"""

    parent = page.get_parent()
    expertise = []
    for i in page.related_area_of_expertise.all().select_related("area_of_expertise"):
        if parent:
            expertise.append(
                {
                    "title": i.area_of_expertise.title,
                    "link": f"{parent.url}?expertise={i.area_of_expertise.slug}",
                }
            )
        else:
            expertise.append({"title": i.area_of_expertise.title})
    return expertise


def get_staff_research_projects(page):
    """Yields pages combining project pages editorially-selected on the staff page,
    and those on which the staff member is listed as lead or a team member
    """
    # ProjectPage model loaded like this to avoid circular import error
    ProjectPage = apps.get_model("projects", "ProjectPage")
    related_project_page_ids = []

    # First return any editorially-highlighted project pages
    for p in page.related_project_pages.all():
        related_project_page_ids.append(p.page.id)
        yield p.page.specific

    # Then return any other project pages which the staff member leads or is a team member of,
    # filtering out any of the highlights already output
    yield from ProjectPage.objects.filter(
        Q(project_lead__page_id=page.pk) | Q(related_staff__page_id=page.pk)
    ).exclude(pk__in=related_project_page_ids).order_by(
        "-first_published_at"
    ).distinct()


def get_student_research_projects(page):
    """Yields pages combining project pages editorially-selected,
    and those on which the student is listed as a team member
    """
    # ProjectPage model loaded like this to avoid circular import error
    ProjectPage = apps.get_model("projects", "ProjectPage")
    related_project_page_ids = []

    # First return any editorially-highlighted project pages
    for p in page.related_project_pages.all():
        related_project_page_ids.append(p.page.id)
        yield p.page.specific

    # Then return any other project pages which the student is a team member of,
    # filtering out any of the highlights already output
    yield from ProjectPage.objects.filter(
        related_student_pages__page_id=page.pk
    ).exclude(pk__in=related_project_page_ids).order_by(
        "-first_published_at"
    ).distinct()


class PerUserContentPanels(ObjectList):
    def _replace_children_with_per_user_config(self):
        if self.request.user.groups.filter(name="Students").exists():
            if self.classname == "content":
                self.children = self.instance.basic_content_panels
            if self.classname == "key_details":
                self.children = self.instance.basic_key_details_panels
            elif self.classname in ["promote", "settings"]:
                self.children = []
        else:
            if self.classname == "content":
                self.children = self.instance.superuser_content_panels
            if self.classname == "key_details":
                self.children = self.instance.key_details_panels

        self.children = [
            child.bind_to(
                model=self.model,
                instance=self.instance,
                request=self.request,
                form=self.form,
            )
            for child in self.children
        ]

    def on_instance_bound(self):
        # replace list of children when both instance and request are available
        if self.request:
            self._replace_children_with_per_user_config()
        else:
            super().on_instance_bound()

    def on_request_bound(self):
        # replace list of children when both instance and request are available
        if self.instance:
            self._replace_children_with_per_user_config()
        else:
            super().on_request_bound()


class PerUserPageMixin:
    basic_content_panels = []
    superuser_content_panels = []

    @cached_classmethod
    def get_edit_handler(cls):
        tabs = []

        if cls.basic_content_panels and cls.superuser_content_panels:
            tabs.append(PerUserContentPanels(heading="Content", classname="content"))
        if cls.key_details_panels and cls.basic_key_details_panels:
            tabs.append(
                PerUserContentPanels(
                    cls.settings_panels, heading="Key Details", classname="key_details"
                )
            )
        if cls.promote_panels:
            tabs.append(
                PerUserContentPanels(
                    cls.promote_panels, heading="Promote", classname="promote"
                )
            )
        if cls.settings_panels:
            tabs.append(
                PerUserContentPanels(
                    cls.settings_panels, heading="Settings", classname="settings"
                )
            )

        edit_handler = TabbedInterface(tabs, base_form_class=cls.base_form_class)

        return edit_handler.bind_to(model=cls)
