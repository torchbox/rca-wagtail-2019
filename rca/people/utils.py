from django.apps import apps
from django.db.models import Q
from wagtail.admin.panels import InlinePanel, ObjectList


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


class StudentPageInlinePanel(InlinePanel):
    """
    InlinePanel that is populated editorially by superusers only. Students
    cannot add, edit, or delete its content, so it's hidden from their view
    entirely rather than showing an empty, non-interactive panel.

    This is done with a CSS class (`w-hidden`) rather than `is_shown()`,
    because `is_shown() == False` stops the panel - including its formset's
    management form - from being rendered into the page at all, which
    breaks form submission ("ManagementForm data is missing or has been
    tampered with") for students even though they never touched this panel.
    """

    class BoundPanel(InlinePanel.BoundPanel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = "admin/panels/student_page_inline_panel.html"

        def classes(self):
            classes = super().classes()
            if self.request.user.is_student():
                classes = classes + ["w-hidden"]
            return classes

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context)
            context["request"] = self.request
            return context


class StudentPagePromoteTab(ObjectList):
    """ObjectList that is hidden entirely from students, as they have no
    permission to edit any of its fields.

    Hidden with a CSS class (`w-hidden`) rather than `is_shown()`: the tab
    contains the required `slug` field (rendered as a hidden input for
    students - see StudentPageAdminForm), and `is_shown() == False` would
    stop it being rendered into the page at all, breaking submission.
    """

    class BoundPanel(ObjectList.BoundPanel):
        def classes(self):
            classes = super().classes()
            if self.request.user.is_student():
                classes = classes + ["w-hidden"]
            return classes


class StudentPageSettingsTab(ObjectList):
    # ObjectList that only displays selected fields to Students
    # As a side effect: If all fields are hidden, the panel is hidden for Students

    class BoundPanel(ObjectList.BoundPanel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            if not self.request.user.is_student():
                return

            for child in self.children:
                if child.panel.__class__.__name__ == "PublishingPanel":
                    for field_row_panel in child.children:
                        if field_row_panel.panel.__class__.__name__ == "FieldRowPanel":
                            # Theres a FieldRowPanel inside the PublishingPanel
                            # Hide it for students by overriding this bound panel's
                            # is_shown (per-request instance, not the shared panel
                            # definition - the previous approach mutated
                            # `field_row_panel.permission` on the Panel definition,
                            # which is bound once and shared across all requests).
                            # Since Wagtail 5.1, a FieldRowPanel would have no children here
                            # The bugfix here: https://docs.wagtail.org/en/stable/releases/5.1.1.html#bug-fixes
                            # seems to be when it was changed.
                            field_row_panel.is_shown = lambda: False
