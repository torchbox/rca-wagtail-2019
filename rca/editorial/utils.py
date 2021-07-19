def get_linked_taxonomy(page, request):
    """Function to generate a list of taxonomy/page relationships
    as links.

    If the EditorialPage we are viewing has a parent listing page then we
    can link the taxonomy items to the parent listing page and apply them
    as filter values.

    Since an editorial page can be placed anywhere in the site, this won't
    always be the case so we need to allow these taxonomy terms to not link.

    Args:
        page :EditorialPage object
        request

    Returns:
        list: Containing taxonomy terms for the template
    """
    taxonomy_tags = []
    editorial_listing_parent = False
    related_schools = page.related_schools.all()
    research_centres = page.related_research_centre_pages.all()
    directorates = page.related_directorates.all()
    parent = page.get_parent().specific

    if parent.__class__.__name__ == "EditorialListingPage":
        editorial_listing_parent = True

    if related_schools:
        for item in related_schools:
            if editorial_listing_parent:
                taxonomy_tags.append(
                    {
                        "title": item.page.title,
                        "link": f"{parent.url}?school-centre-or-area=s-{item.page.slug}",
                    }
                )
            else:
                taxonomy_tags.append({"title": item.page})

    if research_centres:
        for item in research_centres:
            if editorial_listing_parent:
                taxonomy_tags.append(
                    {
                        "title": item.page.title,
                        "link": f"{parent.url}?school-centre-or-area=c-{item.page.slug}",
                    }
                )
            else:
                taxonomy_tags.append({"title": item.page})

    if directorates:
        for item in directorates:
            if editorial_listing_parent:
                taxonomy_tags.append(
                    {
                        "title": item.directorate.title,
                        "link": f"{parent.url}?school-centre-or-area=d-{item.directorate.slug}",
                    }
                )
            else:
                taxonomy_tags.append({"title": item.directorate.title})

    return taxonomy_tags
