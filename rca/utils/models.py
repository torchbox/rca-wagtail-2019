from django.core.exceptions import ValidationError
from django.db import models
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from wagtail.admin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet

from rca.utils.cache import get_default_cache_control_decorator


class LinkFields(models.Model):
    """
    Adds fields for internal and external links with some methods to simplify the rendering:

    <a href="{{ obj.get_link_url }}">{{ obj.get_link_text }}</a>
    """

    link_page = models.ForeignKey(
        "wagtailcore.Page", blank=True, null=True, on_delete=models.SET_NULL
    )
    link_url = models.URLField(blank=True)
    link_text = models.CharField(blank=True, max_length=255)

    class Meta:
        abstract = True

    def clean(self):
        if not self.link_page and not self.link_url:
            raise ValidationError(
                {
                    "link_url": ValidationError(
                        "You must specify link page or link url."
                    ),
                    "link_page": ValidationError(
                        "You must specify link page or link url."
                    ),
                }
            )

        if self.link_page and self.link_url:
            raise ValidationError(
                {
                    "link_url": ValidationError(
                        "You must specify link page or link url. You can't use both."
                    ),
                    "link_page": ValidationError(
                        "You must specify link page or link url. You can't use both."
                    ),
                }
            )

        if not self.link_page and not self.link_text:
            raise ValidationError(
                {
                    "link_text": ValidationError(
                        "You must specify link text, if you use the link url field."
                    )
                }
            )

    def get_link_text(self):
        if self.link_text:
            return self.link_text

        if self.link_page:
            return self.link_page.title

        return ""

    def get_link_url(self):
        if self.link_page:
            return self.link_page.get_url

        return self.link_url

    panels = [
        MultiFieldPanel(
            [
                PageChooserPanel("link_page"),
                FieldPanel("link_url"),
                FieldPanel("link_text"),
            ],
            "Link",
        )
    ]


# Related pages
class RelatedPage(Orderable, models.Model):
    page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )

    class Meta:
        abstract = True
        ordering = ["sort_order"]

    panels = [PageChooserPanel("page")]


class RelatedStaffPageWithManualOptions(Orderable):
    """ This is in preparation for swapping to an internal page selection in the future
    so the page selction is not offered at the moment """

    page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )

    image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    first_name = models.CharField(max_length=125)
    surname = models.CharField(max_length=125)
    role = models.CharField(max_length=125, blank=True)
    description = models.TextField(
        blank=True, help_text="Not displayed for small teaser profiles"
    )
    link = models.URLField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ["sort_order"]

    panels = [
        ImageChooserPanel("image"),
        FieldPanel("first_name"),
        FieldPanel("surname"),
        FieldPanel("role"),
        FieldPanel("description"),
        FieldPanel("link"),
    ]


# Generic social fields abstract class to add social image/text to any new content type easily.
class SocialFields(models.Model):
    social_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    social_text = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True

    promote_panels = [
        MultiFieldPanel(
            [ImageChooserPanel("social_image"), FieldPanel("social_text")],
            "Social networks",
        )
    ]


# Generic listing fields abstract class to add listing image/text to any new content type easily.
class ListingFields(models.Model):
    listing_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Choose the image you wish to be displayed when this page appears in listings",
    )
    listing_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Override the page title used when this page appears in listings",
    )
    listing_summary = models.CharField(
        max_length=255,
        blank=True,
        help_text="The text summary used when this page appears in listings. It's also used as "
        "the description for search engines if the 'Search description' field above is not defined.",
    )

    class Meta:
        abstract = True

    promote_panels = [
        MultiFieldPanel(
            [
                ImageChooserPanel("listing_image"),
                FieldPanel("listing_title"),
                FieldPanel("listing_summary"),
            ],
            "Listing information",
        )
    ]


@register_snippet
class CallToActionSnippet(models.Model):
    title = models.CharField(max_length=255)
    summary = RichTextField(blank=True, max_length=255)
    image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    link = StreamField(
        blocks.StreamBlock(
            [
                (
                    "external_link",
                    blocks.StructBlock(
                        [("url", blocks.URLBlock()), ("title", blocks.CharBlock())],
                        icon="link",
                    ),
                ),
                (
                    "internal_link",
                    blocks.StructBlock(
                        [
                            ("page", blocks.PageChooserBlock()),
                            ("title", blocks.CharBlock(required=False)),
                        ],
                        icon="link",
                    ),
                ),
            ],
            max_num=1,
            required=True,
        ),
        blank=True,
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("summary"),
        ImageChooserPanel("image"),
        StreamFieldPanel("link"),
    ]

    def get_link_text(self):
        # Link is required, so we should always have
        # an element with index 0
        block = self.link[0]

        title = block.value["title"]
        if block.block_type == "external_link":
            return title

        # Title is optional for internal_link
        # so fallback to page's title, if it's empty
        return title or block.value["page"].title

    def get_link_url(self):
        # Link is required, so we should always have
        # an element with index 0
        block = self.link[0]

        if block.block_type == "external_link":
            return block.value["url"]

        return block.value["page"].get_url()

    def __str__(self):
        return self.title


@register_setting
class SocialMediaSettings(BaseSetting):
    twitter_handle = models.CharField(
        max_length=255,
        blank=True,
        help_text="Your Twitter username without the @, e.g. katyperry",
    )
    facebook_app_id = models.CharField(
        max_length=255, blank=True, help_text="Your Facebook app ID."
    )
    facebook_page_name = models.CharField(
        max_length=255, blank=True, help_text="Your Facebook Page URL e.g. torchbox"
    )
    instagram = models.CharField(
        max_length=255, blank=True, help_text="Your Instagram username."
    )
    youtube = models.CharField(
        max_length=255, blank=True, help_text="Your YouTube username."
    )
    linkedin_url = models.URLField(
        blank=True, help_text="Your full Linked in page url."
    )
    default_sharing_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Default sharing text to use if social text has not been set on a page.",
    )
    site_name = models.CharField(
        max_length=255,
        blank=True,
        default="RCA Website",
        help_text="Site name, used by Open Graph.",
    )


@register_setting
class SystemMessagesSettings(BaseSetting):
    class Meta:
        verbose_name = "system messages"

    title_404 = models.CharField("Title", max_length=255, default="Page not found")
    body_404 = RichTextField(
        "Text",
        default="<p>You may be trying to find a page that doesn&rsquo;t exist or has been moved.</p>",
    )

    panels = [
        MultiFieldPanel([FieldPanel("title_404"), FieldPanel("body_404")], "404 page")
    ]


# Apply default cache headers on this page model's serve method.
@method_decorator(get_default_cache_control_decorator(), name="serve")
class BasePage(SocialFields, ListingFields, Page):
    show_in_menus_default = True

    class Meta:
        abstract = True

    promote_panels = (
        Page.promote_panels + SocialFields.promote_panels + ListingFields.promote_panels
    )


class OptionalLink(models.Model):
    link_url = models.URLField(blank=True)
    link_title = models.CharField(blank=True, max_length=125)

    class Meta:
        abstract = True

    panels = [
        MultiFieldPanel(
            [FieldPanel("link_url"), FieldPanel("link_title")], heading="Optional link"
        )
    ]

    def clean(self):
        if self.link_url and not self.link_title:
            raise ValidationError(
                {"link_title": ValidationError("You must specify text for the link.")}
            )
        if self.link_title and not self.link_url:
            raise ValidationError(
                {"link_url": ValidationError("You must specify a URL for the link.")}
            )


@register_snippet
class FacilitiesSnippet(OptionalLink):
    admin_title = models.CharField(
        max_length=255,
        help_text="The title value is only used to identify the snippet in the admin interface ",
    )
    introduction = models.CharField(max_length=255)
    copy = models.TextField(blank=True)

    panels = [
        FieldPanel("admin_title"),
        FieldPanel("introduction"),
        FieldPanel("copy"),
    ] + OptionalLink.panels

    def __str__(self):
        return self.admin_title


@register_snippet
class StepSnippet(OptionalLink):
    admin_title = models.CharField(
        max_length=255,
        help_text="The title value is only used to identify the snippet in the admin interface ",
    )

    heading = models.CharField(max_length=500)

    panels = [FieldPanel("admin_title"), FieldPanel("heading")] + OptionalLink.panels

    def __str__(self):
        return self.admin_title


@register_snippet
class AccordionSnippet(OptionalLink):
    heading = models.CharField(
        help_text="A large heading diplayed next to the block",
        blank=True,
        max_length=125,
    )
    admin_title = models.CharField(
        max_length=255,
        help_text="The title value is only used to identify the snippet in the admin interface ",
    )
    preview_text = models.CharField(
        help_text="The text to display when the accordion is collapsed",
        blank=True,
        max_length=250,
    )
    body = RichTextField(
        help_text="The content shown when the accordion expanded",
        features=["h2", "h3", "bold", "italic", "image", "ul", "ol", "link"],
    )

    def __str__(self):
        return self.admin_title

    panels = [
        FieldPanel("admin_title"),
        FieldPanel("heading"),
        FieldPanel("preview_text"),
        FieldPanel("body"),
    ] + OptionalLink.panels


@register_snippet
class FeeDisclaimerSnippet(models.Model):
    text = models.TextField(blank=True)
    admin_title = models.CharField(
        max_length=255,
        help_text="The title value is only used to identify the snippet in the admin interface ",
    )

    def __str__(self):
        return self.admin_title

    panels = [FieldPanel("admin_title"), FieldPanel("text")]


@register_setting
class ProgrammeSettings(BaseSetting):
    class Meta:
        verbose_name = "Programme settings"

    disable_apply_tab = models.BooleanField(
        default=0,
        help_text=(
            "This setting will remove the apply tab from all programme pages. "
            "This setting overrides the same setting applied at the individual programme page level."
        ),
    )

    panels = [
        MultiFieldPanel(
            [FieldPanel("disable_apply_tab")], "Global settings for programme pages"
        )
    ]


FAQ = 1
TC = 2
SHORT_COURSE_DETAIL_TYPES = [(FAQ, "FAQs"), (TC, "T&Cs")]


@register_snippet
class ShortCourseDetailSnippet(models.Model):
    snippet_type = models.PositiveSmallIntegerField(choices=(SHORT_COURSE_DETAIL_TYPES))
    title = models.CharField(
        max_length=255,
        help_text="Used only in the CMS to identify this particular snippet.",
    )
    url = models.URLField()

    panels = [FieldPanel("snippet_type"), FieldPanel("title"), FieldPanel("url")]

    def __str__(self):
        return self.title

    def body(self):
        if self.snippet_type == FAQ:
            return format_html(
                f'<p>For more information, please visit our <a href="{self.url}">FAQs</a> before applying.</p>'
            )
        if self.snippet_type == TC:
            return format_html(
                f'<p>Please be sure to read our <a href="{self.url}">Terms & Conditions</a> before applying.</p>'
            )


class ResearchType(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.title
