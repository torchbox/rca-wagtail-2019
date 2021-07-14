def get_linked_taxonomy(page, parent, request):
    """Function to generate a list of taxonomy/page relationships
    as links.

    If the EditorialPage we are viewing has a parent listing page then we
    can link the taxonomy items to the parent listing page and apply them
    as filter values.

    Since an editorial page can be placed anywhere in the site, this won't
    always be the case so we need to allow these taxonomy terms to not link.

    Args:
        page :EditorialPage object
        parent: The EditorialPage parent object
        request

    Returns:
        list: Containing taxonomy terms for the template
    """
    editorial_listing_parent = False
    if parent.__class__.__name__ == "EditorialListingPage":
        editorial_listing_parent = True

    taxonomy_tags = []
    if page.related_schools.exists():
        for item in page.related_schools.all():
            if editorial_listing_parent:
                taxonomy_tags.append(
                    {
                        "title": item.page.title,
                        "link": f"{parent.url}?school-centre-or-area=s-{item.page.slug}",
                    }
                )
            else:
                taxonomy_tags.append({"title": item.page})

    if page.related_research_centre_pages.exists():
        for item in page.related_research_centre_pages.all():
            if editorial_listing_parent:
                taxonomy_tags.append(
                    {
                        "title": item.page.title,
                        "link": f"{parent.url}?school-centre-or-area=c-{item.page.slug}",
                    }
                )
            else:
                taxonomy_tags.append({"title": item.page})

    if page.related_directorates.exists():
        for item in page.related_directorates.all():
            if editorial_listing_parent:
                taxonomy_tags.append(
                    {
                        "title": item.page.title,
                        "link": f"{parent.url}?school-centre-or-area=d-{item.directorate.slug}",
                    }
                )
            else:
                taxonomy_tags.append({"title": item.page})

    return taxonomy_tags
