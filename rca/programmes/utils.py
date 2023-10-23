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
