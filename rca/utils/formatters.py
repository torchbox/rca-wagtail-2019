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


def format_study_mode(strings, separator=" or "):
    """
    Formats a list of strings by concatenation using the separator.
    If the last word of each string is the same, it is only used once, at the end.

    Args:
        strings (list): List of study mode strings to be formatted.
        separator (str, optional): Separator to be used between formatted parts.
        Defaults to ' or '.

    Returns:
        str: Formatted study mode string.

    Example:
        >>> study_modes = [
        ...     "Full-time study",
        ...     "Part-time study",
        ... ]
        >>> format_study_mode(study_modes)
        'Full-time or part-time study'
        >>> study_modes = [
        ...     "Full-time",
        ...     "Part-time",
        ... ]
        >>> format_study_mode(study_modes)
        'Full-time or part-time'
    """
    words_list = [string.split() for string in strings]
    last_words = [words[-1].lower() for words in words_list]
    last_words_are_common = all(word == last_words[0] for word in last_words)

    if last_words_are_common:
        common_word = last_words[0]
        # get the first part of each string (excluding the common word)
        formatted_string = [
            string[: -len(common_word)].strip().capitalize() for string in strings
        ]

        result = separator.join(formatted_string) + " " + common_word

        return result.capitalize()
    else:
        return separator.join(strings).capitalize()
