def news_teaser_formatter(item, image=None):
    item_as_dict = {}

    editorial_type = item.editorial_types.first()
    item_as_dict["type"] = editorial_type.type if editorial_type else ""

    if image and item.hero_image:
        item_as_dict["image"] = item.hero_image.get_rendition("fill-392x284").url
        item_as_dict["image_alt"] = item.hero_image.alt
    item_as_dict["formatted_date"] = item.published_at
    item_as_dict["title"] = item.title
    item_as_dict["link"] = item.url

    return item_as_dict


def event_teaser_formatter(item, image=None):
    item_as_dict = {"type": item.event_type or ""}

    if image and item.hero_image:
        item_as_dict["image"] = item.hero_image.get_rendition("fill-392x284").url
        item_as_dict["image_alt"] = item.hero_image.alt
    item_as_dict["formatted_date"] = (
        str(item.start_date.strftime("%-d %b %Y")) + ", Location (TODO)"
    )
    item_as_dict["title"] = item.title
    item_as_dict["link"] = item.url

    return item_as_dict
