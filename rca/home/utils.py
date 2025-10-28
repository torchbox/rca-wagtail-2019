from rca.utils.models import get_listing_image


def related_news_events_formatter(
    page, long_description=False, editorial_meta_label=""
):
    if not page:
        return {}

    # Organsises data into a digestable format for the template.
    editorial_meta = editorial_meta_label
    PAGE_META_MAPPING = {
        "EditorialPage": editorial_meta,
        "EventDetailPage": "Event",
    }
    editorial_published_date = getattr(page, "published_at", None)
    if editorial_published_date and not long_description:
        editorial_description = editorial_published_date.strftime("%-d %B %Y")
    else:
        editorial_description = page.introduction

    PAGE_DESCRIPTION_MAPPING = {
        "EditorialPage": editorial_description,
        "EventDetailPage": getattr(page, "event_date_short", None),
    }
    meta = PAGE_META_MAPPING.get(page.__class__.__name__, "")
    description = PAGE_DESCRIPTION_MAPPING.get(page.__class__.__name__, "")
    try:
        image = get_listing_image(page).get_rendition("fill-878x472").url
    except AttributeError:
        image = None
    return {
        "image": image,
        "title": page.title,
        "link": page.url,
        "description": description,
        "type": meta,
    }


def partnerships_slides_formatter(slides):
    # The partnerships.slides field offers choice between a page
    # or a custom teaser, this method formats the data so either values
    # can be sent to the homepage template and format into a slideshow.
    formatted_slides = []

    for slide in slides:
        if slide.block_type == "custom_teaser":
            formatted_slides.append(
                {
                    "value": {
                        "title": slide.value["title"],
                        "summary": slide.value["text"],
                        "image": slide.value["image"],
                        "link": slide.value["link"]["url"],
                        "type": slide.value["meta"],
                    }
                }
            )
        elif slide.block_type == "page":
            if not slide.value:
                continue

            page_type = None
            page_type_mapping = {
                "GuidePage": "GUIDE",
                "ProjectPage": "PROJECT",
                "ResearchCentrePage": "RESEARCH CENTRE",
                "ShortCoursePage": "SHORT COURSE",
                "ProgrammePage": "PROGRAMME",
            }
            page = slide.value.specific

            if page.__class__.__name__ in page_type_mapping:
                page_type = page_type_mapping.get(page.__class__.__name__, None)
            summary = (
                page.introduction
                if hasattr(page, "introduction")
                else page.listing_summary
            )
            image = (
                page.hero_image if hasattr(page, "hero_image") else page.listing_image
            )
            formatted_slides.append(
                {
                    "value": {
                        "title": page.title,
                        "summary": summary,
                        "image": image,
                        "link": page.url,
                        "type": page_type,
                    }
                }
            )

    return formatted_slides
