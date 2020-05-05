from urllib.parse import urlparse

from django import template
from django.conf import settings
from wagtail.core.utils import camelcase_to_underscore

from rca.utils.models import SocialMediaSettings

register = template.Library()


# Social text
@register.filter(name="social_text")
def social_text(page, site):
    try:
        return page.social_text
    except AttributeError:
        return SocialMediaSettings.for_site(site).default_sharing_text


# Get widget type of a field
@register.filter(name="widget_type")
def widget_type(bound_field):
    return camelcase_to_underscore(bound_field.field.widget.__class__.__name__)


# Get type of field
@register.filter(name="field_type")
def field_type(bound_field):
    return camelcase_to_underscore(bound_field.field.__class__.__name__)


# Get Sitewide social settings
@register.simple_tag(takes_context=True)
def social_media_links(context):
    settings = context["settings"]
    twitter_url = (
        "http://twitter.com/%s"
        % settings["utils"]["SocialMediaSettings"].twitter_handle
        if settings["utils"]["SocialMediaSettings"].twitter_handle
        else False
    )
    twitter = {"url": twitter_url, "type": "twitter", "label": "Twitter"}
    facebook_url = (
        "http://facebook.com/%s"
        % settings["utils"]["SocialMediaSettings"].facebook_page_name
        if settings["utils"]["SocialMediaSettings"].facebook_page_name
        else False
    )
    facebook = {"url": facebook_url, "type": "facebook", "label": "Facebook"}
    instagram_url = (
        "http://instagram.com/%s" % settings["utils"]["SocialMediaSettings"].instagram
        if settings["utils"]["SocialMediaSettings"].instagram
        else False
    )
    instagram = {"url": instagram_url, "type": "instagram", "label": "Instagram"}
    youtube_url = (
        "http://youtube.com/%s" % settings["utils"]["SocialMediaSettings"].youtube
        if settings["utils"]["SocialMediaSettings"].youtube
        else False
    )
    youtube = {"url": youtube_url, "type": "youtube", "label": "YouTube"}
    linkedin = {
        "url": settings["utils"]["SocialMediaSettings"].linkedin_url,
        "type": "linkedin",
        "label": "Linkedin",
    }
    return [twitter, facebook, instagram, youtube, linkedin]


default_domains = [
    settings.BASE_URL,
    "rca-production.herokuapp.com",
    "rca-staging.herokuapp.com",
    "rca-development.herokuapp.com",
    "rca.ac.uk",
    "www.rca.ac.uk",
    "0.0.0.0",
    "localhost",
]


@register.simple_tag(name="is_external")
def is_external(*args):
    """
    Work out if a url value or firstof values is in the list of default_domains.
    If it isn't, return True. Instead of populating an href and target together,
    which would be preferable, this is for use when adding suitable targets and
    icons for external links

    example single {% is_external 'https://bbc.co.uk' %} would return True
    example empty {% is_external '' '' %} would return False
    example multiple {% is_external 'https://rca.ac.uk' 'https://bbc.co.uk' %} would return False

    Returns:
        Boolean -- True if the url value is not in the list of default domains
    """
    # find the first non empty value
    try:
        link = next(s for s in args if s)
    except StopIteration:
        # incase we get passed empty strings
        return False

    # Pattern library links are all '#' which will be internal.
    if link != "#":
        if urlparse(link).hostname not in default_domains:
            return True

    return False


@register.filter
def slice_pagination(page_range, current_page):
    """Slices paginator.page_range to the sections of page numbers to display
    Examples (total pages 10)

    When current_page is 1
        [[1, 2, 3], [10]]
    When current_page is 2
        [[1, 2, 3], [10]]
    When current_page is 3
        [[1, 2, 3, 4], [10]]
    When current_page is 4-7
        [[1], [3, 4, 5], [10]]
    When current_page is 8
        [[1], [7,8, 9, 10]]
    When current_page is 9
        [[1], [8, 9, 10]]
    When current_page is 10
        [[1], [8, 9, 10]]
    """
    # If there are 4 or less items, just return a list containing 1 section.
    if len(page_range) <= 4:
        return [page_range]

    # Build a list of lists for the different pagination sections
    pagination_pages = []
    current_page_index = page_range.index(current_page)
    current_item = page_range[current_page_index]
    first_item = page_range[0]
    items = []
    last_item = page_range[-1]

    offsets = [-2, -1, 0, 1, 2]
    for offset in offsets:
        try:
            new_item = page_range[current_page_index + offset]
        except IndexError:
            continue
        if offset == 0:
            items.append(new_item)
        elif offset < 0 and new_item < current_item:
            items.append(new_item)
        elif offset > 0 and new_item > current_item:
            items.append(new_item)

    if first_item in items and last_item in items:
        pagination_pages.append(items)
    else:
        if first_item in items:
            new_items = items[:3]
            if new_items.index(current_item) == 2:
                new_items = items[:4]
            pagination_pages.append(new_items)
            pagination_pages.append([last_item])
        elif last_item in items:
            new_items = items[-3:]
            if new_items.index(current_item) == 0:
                new_items = items[-4:]
            pagination_pages.append([first_item])
            pagination_pages.append(new_items)
        else:
            pagination_pages.append([first_item])
            pagination_pages.append(items[1:4])
            pagination_pages.append([last_item])

    return pagination_pages
