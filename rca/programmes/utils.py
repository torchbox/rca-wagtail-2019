from itertools import chain

from rca.utils.models import AccordionSnippet


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


def get_accordion_snippet_content(stream_field):
    """
    Helper function to extract content from a SnippetChooserBlock (for `AccordionSnippet`s)
    in a StreamField.

    Args:
        stream_field (StreamField): A StreamField containing a block of type `accordion_snippet`.

    Returns:
        str or None: A formatted string containing the "heading," "preview_text," and "body"
        fields of the matched AccordionSnippet objects. Returns None if the StreamField is empty
        or does not contain any accordion snippet values.

    Usage:
        Suppose you have the following:

        ```python
        requirements_blocks = StreamField(
            [
                ("accordion_block", AccordionBlockWithTitle()),
                ("accordion_snippet", SnippetChooserBlock("utils.AccordionSnippet")),
            ],
            blank=True,
            verbose_name="Accordion blocks",
        )
        ```

        If you add the `requirements_blocks` StreamField to the search index, the `accordion_snippet`
        will not be indexed, only the `accordion_block` will be indexed.

        Because we cannot directly index the `accordion_snippet` block in the `requirements_blocks`
        StreamField, we have to do this manually. This is where this helper function comes in.

        In your Django model, you can define a method that returns the content of the accordion snippet:

        ```python
        def get_requirements_blocks_accordion_snippet(self):
            return get_accordion_snippet_content(self.requirements_blocks)
        ```

        Then add your method to the search index, in addition to the `requirements_blocks` field:

        ```python
        search_fields = BasePage.search_fields + [
            # ...,
            index.SearchField("requirements_blocks"),
            index.SearchField("get_requirements_blocks_accordion_snippet"),
            # ...,
        ]
        ```

    Reference:
        https://docs.wagtail.org/en/stable/topics/search/indexing.html#indexing-callables-and-other-attributes
    """
    if not stream_field:
        return None

    data = stream_field.get_prep_value()
    accordion_snippet_values = [
        item.get("value") for item in data if item.get("type") == "accordion_snippet"
    ]

    if not accordion_snippet_values:
        return None

    accordion_snippet_content = AccordionSnippet.objects.filter(
        pk__in=accordion_snippet_values
    ).values_list("heading", "preview_text", "body")
    return "\n".join(list(chain(*accordion_snippet_content)))
