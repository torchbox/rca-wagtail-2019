from urllib.parse import urljoin, urlparse

from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core import blocks
from wagtail.core.fields import StreamField


def url_or_relative_url_validator(value):
    if not urlparse(value).netloc:
        value = urljoin("https://rca.ac.uk/", value)
    return validators.URLValidator()(value)


class URLOrRelativeURLFormField(forms.URLField):
    default_validators = [url_or_relative_url_validator]

    def to_python(self, value):
        value = super().to_python(value)
        if value:
            if value.startswith("http:///"):
                value = value[7:]
        return value


class URLOrRelativeURLBLock(blocks.FieldBlock):
    def __init__(
        self,
        required=True,
        help_text=None,
        max_length=None,
        min_length=None,
        validators=(),
        **kwargs
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
    url = URLOrRelativeURLBLock(required=False)
    page = blocks.PageChooserBlock(required=False)
    title = blocks.CharBlock(
        help_text="Leave blank to use the page's own title, required if using a URL",
        required=False,
    )

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
class NavigationSettings(BaseSetting, ClusterableModel):

    primary_navigation = StreamField(
        [("link", PrimaryNavLink())], blank=True, help_text="Main site navigation"
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

    panels = [
        StreamFieldPanel("quick_links"),
        StreamFieldPanel("primary_navigation"),
        StreamFieldPanel("footer_navigation"),
        StreamFieldPanel("footer_links"),
    ]
