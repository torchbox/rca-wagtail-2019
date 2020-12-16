def format_projects_for_gallery(projects):
    """Internal method for formatting related projects to the correct
    structure for the gallery template

    Arguments:
        projects: Queryset of project pages to format

    Returns:
        List: Maximum of 8 projects
    """
    items = []
    for page in projects[:8]:
        page = page.specific
        meta = ""
        related_school = page.related_school_pages.first()
        if related_school is not None:
            meta = related_school.page.title

        items.append(
            {
                "title": page.title,
                "link": page.url,
                "image": page.hero_image,
                "description": page.introduction,
                "meta": meta,
            }
        )
    return items
