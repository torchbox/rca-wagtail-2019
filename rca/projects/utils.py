def format_projects_for_gallery(projects):
    """Global function for formatting related projects to the correct
    structure for the gallery template

    Arguments:
        projects: Queryset of project pages to format

    Returns:
        List: Maximum of 8 projects
    """
    items = []
    projects = projects.prefetch_related("related_school_pages__page")
    projects = projects.prefetch_related("research_types__research_type")
    projects = projects.select_related("hero_image")

    for page in projects[:8]:
        page = page.specific
        
        meta = []
        related_school = page.related_school_pages.first()
        if related_school is not None:
            meta.append(related_school.page.title)
        meta += [t.research_type.title for t in page.research_types.all()]

        items.append(
            {
                "title": page.title,
                "link": page.url,
                "image": page.hero_image,
                "description": page.introduction or page.listing_summary,
                "meta": ", ".join(meta),
            }
        )
    return items
