page_type_mapping = {
    "GuidePage": "GUIDE",
    "ProjectPage": "PROJECT",
    "ResearchCentrePage": "RESEARCH CENTRE",
    "ShortCoursePage": "SHORT COURSE",
    "ProgrammePage": "PROGRAMME",
}


def related_list_block_slideshow(slides):
    # This formatter can be used to render out slides when defined on the model
    # with RelatedPageListBlockPage()
    # E.G slides = StreamField(StreamBlock([("Page", RelatedPageListBlockPage())]))
    # The reason being that custom field data OR internal pages can be referenced
    formated_slides = []
    for slide in slides:
        for block in slide.value:
            if block.block_type == "custom_teaser":
                formated_slides.append(
                    {
                        "value": {
                            "title": block.value["title"],
                            "summary": block.value["text"],
                            "image": block.value["image"],
                            "link": block.value["link"]["url"],
                            "type": block.value["meta"],
                        }
                    }
                )
            elif block.block_type == "page":
                if not block.value:
                    continue

                page = block.value.specific
                page_type = page_type_mapping.get(page.__class__.__name__, None)
                summary = (
                    page.introduction
                    if hasattr(page, "introduction") and page.introduction
                    else page.listing_summary
                )
                image = (
                    page.hero_image
                    if hasattr(page, "hero_image")
                    else page.listing_image
                )
                formated_slides.append(
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
    return formated_slides


def format_page_teasers(obj):
    if not obj:
        return
    page_teasers = {"title": obj.title, "summary": obj.summary, "pages": []}
    for item in obj.pages:
        for block in item.value:
            if block.block_type == "custom_teaser":
                page_teasers["pages"].append(
                    {
                        "title": block.value["title"],
                        "description": block.value["text"],
                        "image": block.value["image"],
                        "link": block.value["link"]["url"],
                        "type": block.value["meta"],
                    }
                )
            elif block.block_type == "page":
                if not block.value:
                    continue

                page = block.value.specific
                summary = (
                    page.introduction
                    if hasattr(page, "introduction")
                    else page.listing_summary
                )
                image = (
                    page.hero_image
                    if hasattr(page, "hero_image")
                    else page.listing_image
                )
                page_teasers["pages"].append(
                    {
                        "title": page.title,
                        "description": summary,
                        "image": image,
                        "link": page.url,
                    }
                )

    return page_teasers
