def format_research_highlights(pages):
    """Function for formatting related projects to the correct
    structure for the gallery template
    Returns:
        List
    """
    items = []
    for page in pages:
        meta = None
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
