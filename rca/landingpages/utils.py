from rca.utils.models import get_listing_image


def news_teaser_formatter(item, return_image=False):
    item_as_dict = {}

    editorial_type = item.editorial_types.first()
    item_as_dict["type"] = editorial_type.type if editorial_type else ""

    listing_image = get_listing_image(item)
    if return_image and listing_image:
        item_as_dict["image"] = listing_image.get_rendition("fill-878x472").url
        item_as_dict["image_alt"] = listing_image.alt
    item_as_dict["formatted_date"] = item.published_at.strftime("%-d %B %Y")
    item_as_dict["title"] = item.title
    item_as_dict["link"] = item.url

    return item_as_dict


def event_teaser_formatter(item, return_image=False):
    item_as_dict = {"type": item.event_type or ""}
    listing_image = get_listing_image(item)
    if return_image and listing_image:
        item_as_dict["image"] = listing_image.get_rendition("fill-878x472").url
        item_as_dict["image_alt"] = listing_image.alt
    item_as_dict["formatted_date"] = (
        str(item.start_date.strftime("%-d %B %Y")) + ", Location (TODO)"
    )
    item_as_dict["title"] = item.title
    item_as_dict["link"] = item.url

    return item_as_dict


def editorial_teaser_formatter(item):
    item_as_dict = {}
    editorial_type = item.editorial_types.first()
    item_as_dict["meta"] = editorial_type.type if editorial_type else ""

    image = get_listing_image(item)
    if image:
        item_as_dict["image"] = image
        item_as_dict["image_alt"] = image.alt
    item_as_dict["formatted_date"] = item.published_at
    item_as_dict["title"] = item.title
    item_as_dict["link"] = item.url
    item_as_dict["description"] = item.introduction

    return item_as_dict
