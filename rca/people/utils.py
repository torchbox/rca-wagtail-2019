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
