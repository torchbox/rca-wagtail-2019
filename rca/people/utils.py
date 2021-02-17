from django.apps import apps
from django.db.models import Q


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
