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
    InlinePanel that prevents non-superusers from making changes to the content
    """

    class BoundPanel(InlinePanel.BoundPanel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.template_name = "admin/panels/student_page_inline_panel.html"

            panel_class = self.panel.classname

            # Collapse the panel for non-superusers

            if not self.request.user.is_superuser and "collapsed" not in panel_class:
                self.panel.classname += " collapsed"
            elif self.request.user.is_superuser and "collapsed" in panel_class:
                self.panel.classname = panel_class.replace("collapsed", "")

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context)
            context["request"] = self.request
            return context


class StudentPagePromoteTab(ObjectList):
    # ObjectList that only displays selected fields to Students
    # As a side effect: If all fields are hidden, the panel is hidden for Students

    class BoundPanel(ObjectList.BoundPanel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            allowed_student_fields = ["slug"]
            permission = "superuser"

            if self.request.user.is_student:

                children = self.panel.children  # multi field panels
                for child in children:
                    panels = child.children  # single field panels
                    for panel in panels:
                        if panel.field_name not in allowed_student_fields:
                            panel.permission = permission


class StudentPageSettingsTab(ObjectList):
    # ObjectList that only displays selected fields to Students
    # As a side effect: If all fields are hidden, the panel is hidden for Students

    class BoundPanel(ObjectList.BoundPanel):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            permission = "superuser"

            if self.request.user.is_student:

                for child in self.panel.children:
                    if child.__class__.__name__ == "PublishingPanel":
                        for field_row_panel in child.children:
                            if field_row_panel.__class__.__name__ == "FieldRowPanel":
                                # Theres a FieldRowPanel inside the PublishingPanel
                                field_row_panel.permission = permission
                                # Since Wagtail 5.1, a FieldRowPanel would have no children here
                                # The bugfix here: https://docs.wagtail.org/en/stable/releases/5.1.1.html#bug-fixes
                                # seems to be when it was changed.
                    # the elif's below are not required, but are here for clarity
                    elif child.__class__.__name__ == "PrivacyModalPanel":
                        pass  # Do nothing so they are still visible
                    elif child.__class__.__name__ == "CommentPanel":
                        pass  # Do nothing so they are still visible
