from django import template
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
