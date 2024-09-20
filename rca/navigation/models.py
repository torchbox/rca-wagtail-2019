from urllib.parse import urljoin, urlparse, urlsplit, urlunsplit

from django import forms
from django.core import validators
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.forms.utils import ErrorList
from modelcluster.models import ClusterableModel
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import StreamField
from wagtail.models import Page


def url_or_relative_url_validator(value):
    if not urlparse(value).netloc:
        # The rca domain here is just for validation sake
        value = urljoin("https://rca.ac.uk/", value)
    return validators.URLValidator()(value)


class URLOrRelativeURLFormField(forms.URLField):
    default_validators = [url_or_relative_url_validator]

    def to_python(self, value):
        value = super().to_python(value)
        if value:
            url_fields = list(urlsplit(value))
            # If netloc (domain) is empty, delete the scheme
            if not url_fields[1]:
                url_fields[0] = ""
            value = urlunsplit(url_fields)
        return value


class URLOrRelativeURLBLock(blocks.FieldBlock):
    def __init__(
        self,
        required=True,
        help_text=None,
        max_length=None,
        min_length=None,
        validators=(),
        **kwargs,
    ):
        self.field = URLOrRelativeURLFormField(
            required=required,
            help_text=help_text,
            max_length=max_length,
            min_length=min_length,
            validators=validators,
        )
        super().__init__(**kwargs)

    class Meta:
        icon = "site"


class LinkBlock(blocks.StructBlock):
    # URL block uses the URLOrRelativeURLBLock so it can accpet relative URLs
    # E.G, /schools/
    url = URLOrRelativeURLBLock(required=False, label="URL")
    page = blocks.PageChooserBlock(required=False)
    title = blocks.CharBlock(
        help_text="Leave blank to use the page's own title, required if using a URL",
        required=False,
    )

    # Add a page url for the page object
    def get_api_representation(self, value, context=None):
        value = {
            name: self.child_blocks[name].get_api_representation(val, context=context)
            for name, val in value.items()
        }

        if value["page"] and not value["url"]:
            # Stale cache data could store a deleted page ID, so try the get
            # query first
            try:
                page = Page.objects.get(id=value["page"])
            except ObjectDoesNotExist:
                # If we can't get the page, it has no business being in the menu
                return []
            value["url"] = page.url
            if not value["title"]:
                value["title"] = page.title

        return value

    def clean(self, value):
        try:
            result = super().clean(value)
        except ValidationError as e:
            errors = e.params
        else:
            errors = {}

        if (value["url"] and value["page"]) or (not value["url"] and not value["page"]):
            errors["url"] = ErrorList(["Please select a URL or a Page"])
        if value["url"] and not value["title"]:
            errors["url"] = ErrorList(["Please set a title when using a URL"])

        if errors:
            raise ValidationError("Validation error in LinkBlock", params=errors)
        return result


class SecondaryLinkBlock(LinkBlock):
    tertiary_links = blocks.ListBlock(LinkBlock())


class QuickLinkBlock(LinkBlock):
    sub_text = blocks.CharBlock(required=False)


class PrimaryNavLink(blocks.StructBlock):
    primary_link = LinkBlock(label="Top level menu links")
    secondary_links = blocks.ListBlock(SecondaryLinkBlock())


@register_setting(icon="list-ul")
class NavigationSettings(BaseSiteSetting, ClusterableModel):

    primary_navigation = StreamField(
        [("link", PrimaryNavLink())],
        blank=True,
        help_text="Main site navigation",
    )

    quick_links = StreamField([("link", QuickLinkBlock())], blank=True)

    footer_navigation = StreamField(
        [("link", LinkBlock())],
        blank=True,
        help_text="Multiple columns of footer links with optional header.",
    )
    footer_links = StreamField(
        [("link", LinkBlock())],
        blank=True,
        help_text="Single list of elements at the base of the page.",
    )

    last_updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("quick_links"),
        FieldPanel("primary_navigation"),
        FieldPanel("footer_navigation"),
        FieldPanel("footer_links"),
    ]

    api_fields = [
        APIField("quick_links"),
        APIField("primary_navigation"),
        APIField("footer_navigation"),
        APIField("footer_links"),
    ]
