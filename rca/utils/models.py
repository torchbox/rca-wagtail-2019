from collections import defaultdict

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.text import slugify
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import ItemBase, TagBase
from wagtail.admin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.api import APIField
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet

from rca.api_content.content import CantPullFromRcaApi, pull_tagged_news_and_events
from rca.utils.cache import get_default_cache_control_decorator

LIGHT_TEXT_ON_DARK_IMAGE = 1
DARK_TEXT_ON_LIGHT_IMAGE = 2
DARK_HERO = "dark"
LIGHT_HERO = "light"

HERO_COLOUR_CHOICES = (
    (LIGHT_TEXT_ON_DARK_IMAGE, "Light text on dark image"),
    (DARK_TEXT_ON_LIGHT_IMAGE, "dark text on light image"),
)


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

        return

    def get_link_url(self):
        if self.link_page:
            return self.link_page.get_url()

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
        blank=False,
        on_delete=models.CASCADE,
        related_name="+",
    )

    class Meta:
        abstract = True
        ordering = ["sort_order"]

    panels = [PageChooserPanel("page")]


class RelatedStaffPageWithManualOptions(Orderable):
    """This is in preparation for swapping to an internal page selection in the future
    so the page selction is not offered at the moment"""

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
    first_name = models.CharField(max_length=125, blank=True)
    surname = models.CharField(max_length=125, blank=-True)
    role = models.CharField(max_length=125, blank=True)
    description = models.TextField(
        blank=True, help_text="Not displayed for small teaser profiles"
    )
    link = models.URLField(blank=True)

    def get_name(self):
        if self.first_name:
            return self.first_name
        elif self.page:
            return self.page.title
        else:
            return self.id

    def __str__(self):
        return self.get_name()

    class Meta:
        abstract = True
        ordering = ["sort_order"]

    # Validation.
    # Only allow adding a related staff page, or the inline fields.

    panels = [
        PageChooserPanel("page", page_type="people.StaffPage"),
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


class LegacySiteTag(TagBase):
    class Meta:
        verbose_name = "legacy site tag"
        verbose_name_plural = "legacy site tags"


class LegacySiteTaggedPage(ItemBase):
    tag = models.ForeignKey(
        LegacySiteTag, related_name="tagged_pages", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to=Page, on_delete=models.CASCADE, related_name="tagged_items"
    )


class LegacyNewsAndEventsMixin(models.Model):
    legacy_news_and_event_tags = ClusterTaggableManager(
        verbose_name="Legacy news and events tags",
        help_text=(
            "Specify one or more tags to identify related news and events from "
            "the legacy site. A maximum of three items with the same combination "
            "of tags will then be displayed on the page."
        ),
        through=LegacySiteTaggedPage,
        blank=True,
    )

    class Meta:
        abstract = True

    @property
    def legacy_news_cache_key(self):
        return f"{self.pk}-legacy-news-and-events"

    def refetch_legacy_news_and_events(self):
        """
        Fetches the related news and events for this page from
        the legacy site. The result is cached to reduce real-time
        calls to the legacy API.
        """
        tags = self.legacy_news_and_event_tags.all().values_list("name", flat=True)
        value = pull_tagged_news_and_events(*tags)
        cache.set(self.legacy_news_cache_key, value, None)
        return value

    @cached_property
    def legacy_news_and_events(self):
        """
        Return a list of news and events from the legacy site
        that are tagged with all of the tags from this
        page's ``legacy_news_and_event_tags``.

        The cached_property decorator is used so that
        ``page.legacy_news_and_events`` can be referenced in the
        template multiple times without triggering another
        cache lookup.
        """
        cached_val = cache.get(self.legacy_news_cache_key)
        if cached_val is not None:
            return cached_val
        return self.refetch_legacy_news_and_events()

    def save(self, *args, **kwargs):
        """
        Overrides the default Page.save() method to trigger
        a cache refresh for legacy news and events (in
        case the tags for this page have changed).
        """
        super().save(*args, **kwargs)
        try:
            self.refetch_legacy_news_and_events()
        except CantPullFromRcaApi:
            # Legacy API can be a bit unreliable, so don't
            # break here. The management command can update
            # the value next time it runs
            pass


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


@register_snippet
class ShortCourseDetailSnippet(models.Model):
    title = models.CharField(
        max_length=255,
        help_text="Used only in the CMS to identify this particular snippet.",
    )
    content = RichTextField(blank=True, max_length=255, features=["link"])

    panels = [FieldPanel("title"), FieldPanel("content")]

    def __str__(self):
        return self.title


class ResearchType(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=500, blank=True)
    slug = models.SlugField(blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(ResearchType, self).save(*args, **kwargs)


@register_setting
class SitewideAlertSetting(BaseSetting):
    class Meta:
        verbose_name = "Sitewide alert"

    show_alert = models.BooleanField(
        default=False, help_text="Checking this will show the site-wide message"
    )
    message = RichTextField(
        help_text="The message to be shown to all users across the site",
        features=["h2", "h3", "bold", "italic", "link"],
    )

    panels = [FieldPanel("show_alert"), FieldPanel("message")]

    api_fields = [APIField("show_alert"), APIField("message")]


class SluggedTaxonomy(models.Model):
    """Taxonomy model that can be used for taxonomies that need a slug
    as a few are identical
    """

    title = models.CharField(max_length=128)
    slug = models.SlugField(blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(SluggedTaxonomy, self).save(*args, **kwargs)

    class meta:
        abstract = True


class ResearchTheme(SluggedTaxonomy):
    pass


class Sector(SluggedTaxonomy):
    class Meta:
        verbose_name = "Innovation RCA sector"
        verbose_name_plural = "Innovation RCA sectors"


class ContactFieldsMixin(models.Model):
    contact_model_title = models.CharField(
        max_length=120,
        blank=True,
        help_text="Maximum length of 120 characters",
        verbose_name="Contact title",
    )
    contact_model_email = models.EmailField(blank=True, verbose_name="Contact email")
    contact_model_url = models.URLField(blank=True, verbose_name="Contact url")
    contact_model_form = models.ForeignKey(
        "forms.FormPage",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Contact form",
    )
    contact_model_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Contact image",
    )
    contact_model_text = models.CharField(
        max_length=250,
        blank=True,
        help_text="Maximum length of 250 characters",
        verbose_name="Contact text",
    )

    class Meta:
        abstract = True

    def clean(self):
        errors = defaultdict(list)
        VALIDATION_MESSAGE = "Add only one contact method"

        if self.contact_model_email and self.contact_model_url:
            errors["contact_model_email"].append(VALIDATION_MESSAGE)
        if self.contact_model_url and self.contact_model_form:
            errors["contact_model_url"].append(VALIDATION_MESSAGE)
        if self.contact_model_email and self.contact_model_form:
            errors["contact_model_email"].append(VALIDATION_MESSAGE)

        if errors:
            raise ValidationError(errors)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("contact_model_title"),
                FieldPanel("contact_model_email"),
                FieldPanel("contact_model_url"),
                FieldPanel("contact_model_text"),
                PageChooserPanel("contact_model_form"),
                ImageChooserPanel("contact_model_image"),
            ],
            "Contact",
        )
    ]
