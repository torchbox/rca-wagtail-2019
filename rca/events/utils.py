def get_linked_taxonomy(page, request):
    """Function to generate a list of taxonomy/page relationships
    as links.

    Args:
        page :EventPage object
        request

    Returns:
        list: Containing taxonomy terms for the template
    """
    taxonomy_tags = []
    related_schools = page.related_schools.all()
    research_centres = page.related_research_centre_pages.all()
    directorates = page.related_directorates.all()
    parent = page.get_parent().specific

    if related_schools:
        for item in related_schools:
            taxonomy_tags.append(
                {
                    "title": item.page.title,
                    "link": f"{parent.url}?school-centre-or-area=s-{item.page.slug}",
                }
            )

    if research_centres:
        for item in research_centres:
            taxonomy_tags.append(
                {
                    "title": item.page.title,
                    "link": f"{parent.url}?school-centre-or-area=c-{item.page.slug}",
                }
            )

    if directorates:
        for item in directorates:
            taxonomy_tags.append(
                {
                    "title": item.directorate.title,
                    "link": f"{parent.url}?school-centre-or-area=d-{item.directorate.slug}",
                }
            )

    return taxonomy_tags
