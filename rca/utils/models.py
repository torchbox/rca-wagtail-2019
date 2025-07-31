from collections import defaultdict
from itertools import chain

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import ItemBase, TagBase
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    HelpPanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.api import APIField
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from rca.api_content.content import CantPullFromRcaApi
from rca.utils.cache import get_default_cache_control_decorator
from rca.utils.forms import RCAPageAdminForm

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
                FieldPanel("link_page"),
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

    panels = [FieldPanel("page")]


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

    def clean(self):
        errors = defaultdict(list)

        if not self.page and not self.role:
            errors["role"].append(
                _(
                    "If you are not referencing a Staff Page, please add a custom role valiue, E.G 'Tutor'"
                )
            )

        if errors:
            raise ValidationError(errors)

    panels = [
        PageChooserPanel("page", page_type="people.StaffPage"),
        FieldPanel("image"),
        FieldPanel("first_name"),
        FieldPanel("surname"),
        FieldPanel("role"),
        FieldPanel("description"),
        FieldPanel("link"),
    ]

    def first_name_api(self):
        if self.page:
            page = self.page.specific
            return page.first_name
        return self.first_name

    def surname_api(self):
        if self.page:
            page = self.page.specific
            return page.last_name
        return self.surname

    def link_or_page(self):
        if self.page:
            return self.page.full_url
        return self.link

    api_fields = [
        APIField("page"),
        APIField("image"),
        APIField("first_name_api"),
        APIField("surname_api"),
        APIField("role"),
        APIField("description"),
        APIField("link"),
        "link_or_page",
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
            [FieldPanel("social_image"), FieldPanel("social_text")],
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
                FieldPanel("listing_image"),
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
        FieldPanel("image"),
        FieldPanel("link"),
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
class SocialMediaSettings(BaseSiteSetting):
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
    tiktok = models.CharField(
        max_length=255,
        default="royalcollegeofart",
        blank=True,
        help_text="Your TikTok handle without the @, e.g. royalcollegeofart",
    )
    pinterest = models.CharField(
        max_length=255,
        default="royalcollegeofart",
        blank=True,
        help_text="Your Pinterest handle without the @, e.g. royalcollegeofart",
    )
    wechat_url = models.URLField(
        default="https://weixin.qq.com/r/uROQiFHEEwxsrRXr90ar",
        blank=True,
        help_text="Your full WeChat page url.",
    )
    little_red_book_handle = models.CharField(
        max_length=255,
        blank=True,
        help_text="Your Little Red Book handle without the @, e.g. royalcollegeofart",
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
class SystemMessagesSettings(BaseSiteSetting):
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
    base_form_class = RCAPageAdminForm
    show_in_menus_default = True

    class Meta:
        abstract = True

    promote_panels = (
        Page.promote_panels + SocialFields.promote_panels + ListingFields.promote_panels
    )

    api_fields = [
        APIField("listing_image"),
        APIField("listing_title"),
        APIField("listing_summary"),
    ]

    @property
    def meta_title(self):
        return self.seo_title.strip() or self.title

    @property
    def meta_description(self):
        return self.search_description.strip() or self.listing_summary

    def has_vepple_panorama(self):
        """
        Used by `base_page.html` to conditionally import generic Vepple embed JS into
        the head. Will be overridden on page types that support using
        `rca.utils.blocks.VeppleEmbedBlock` in `StreamField` content, and return `True`
        if one is detected in the field's `body` value.
        """
        return False


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


class NewsAndEventsMixin:
    """
    This class is desiged to first work _with_ LegacyNewsAndEventsMixin and
    eventually replace it.

    If a page has no ``legacy_news_and_event_tags`` value, then this class can
    be used to return related editorial and event pages from within this site,
    rather than via the api. The reasoning for this is that publishing editorial
    and event items is likely to take time. Adding this logic means that if and
    when a page in question has enough newly published events end editorial
    pages related, the ``legacy_news_and_event_tags`` value can be set as blank.
    This will be instatiated and internal related page data will be returned.

    """

    def __init__(self, page, *args, **kwargs):
        from rca.editorial.models import EditorialPage
        from rca.events.models import EventDetailPage
        from rca.landingpages.models import LandingPage

        self.event_page_model = EventDetailPage
        self.editorial_page_model = EditorialPage

        self.page = page
        self.editorial_items = 3
        self.page_type = page.__class__.__name__
        self.page_is_landing_page = issubclass(page.__class__, LandingPage)

    def get_editorial_type(self, page):
        editorial_type = getattr(page, "editorial_types", None)
        if editorial_type:
            try:
                return editorial_type.first().type
            except AttributeError:
                return ""

    def format_data(self, pages_queryset):
        """
        Used to turn queryset data into a list of dicts
        for the template
        """
        items = []
        for page in pages_queryset:
            # Quite an elaborate check for the editorial_type to avoid
            # throwing an error when the page here is an EventDetailPage
            editorial_type = self.get_editorial_type(page)

            PAGE_META_MAPPING = {
                "EditorialPage": editorial_type,
                "EventDetailPage": "Event",
            }
            meta = PAGE_META_MAPPING.get(page.__class__.__name__, "")
            editorial_published_date = getattr(page, "published_at", None)

            if editorial_published_date:
                editorial_published_date = editorial_published_date.strftime(
                    "%-d %B %Y"
                )

            PAGE_DESCRIPTION_MAPPING = {
                "EditorialPage": editorial_published_date,
                "EventDetailPage": getattr(page, "event_date_short", None),
            }
            description = PAGE_DESCRIPTION_MAPPING.get(page.__class__.__name__, "")

            image = get_listing_image(page)
            if image:
                image = image.get_rendition("fill-878x472").url
            items.append(
                {
                    "image": image,
                    "title": page.title,
                    "link": page.url,
                    "description": description,
                    "type": meta,
                }
            )
        return items

    def get_landing_page_editorial_and_events(self):
        event = (
            self.event_page_model.objects.live()
            .filter(related_landing_pages__page=self.page)
            .filter(start_date__gte=timezone.now().date())
            .order_by("start_date")[:1]
        )
        if event:
            self.editorial_items = 2

        news = (
            self.editorial_page_model.objects.filter(
                related_landing_pages__page=self.page
            )
            .live()
            .order_by("-published_at")[: self.editorial_items]
        )
        return list(chain(news, event))

    def get_research_page_editorial_and_events(self):
        event = (
            self.event_page_model.objects.live()
            .filter(related_research_centre_pages__page=self.page)
            .filter(start_date__gte=timezone.now().date())
            .order_by("start_date")[:1]
        )
        if event:
            self.editorial_items = 2

        news = (
            self.editorial_page_model.objects.filter(
                related_research_centre_pages__page=self.page
            )
            .live()
            .order_by("-published_at")[: self.editorial_items]
        )
        return list(chain(news, event))

    def get_schools_editorial_and_events(self):
        event = (
            self.event_page_model.objects.live()
            .filter(related_schools__page=self.page)
            .filter(start_date__gte=timezone.now().date())
            .order_by("start_date")[:1]
        )
        if event:
            self.editorial_items = 2

        news = (
            self.editorial_page_model.objects.filter(related_schools__page=self.page)
            .live()
            .order_by("-published_at")[: self.editorial_items]
        )
        return list(chain(news, event))

    def get_data(self):
        if self.page_is_landing_page:
            data = self.format_data(self.get_landing_page_editorial_and_events())
        if self.page_type == "ResearchCentrePage":
            data = self.format_data(self.get_research_page_editorial_and_events())
        elif self.page_type == "SchoolPage":
            data = self.format_data(self.get_schools_editorial_and_events())
        return data

    @property
    def legacy_news_and_events(self):
        """
        Once ready to turn off legacy news and events, all models with
        LegacyNewsAndEventsMixin can be replaced with NewsAndEventsMixin,
        then the legacy_news_and_events method below will be used soley for the
        internal pages that are related. This will make template integration
        easier as this property is already in use on LegacyNewsAndEventsMixin.
        """
        return self.get_data()


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
        Method which used to fetch related news and events from
        the legacy site. This site is now defunct, so this method
        is no longer expected to return anything.

        TODO: remove this and other references in the codebase to
              it or to the legacy news and events content
        """
        return []

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

        If there is no ``page.legacy_news_and_event_tags`` value, it returns
        Editorial and Event pages with relationships to this page via
        utils.NewsAndEventsMixin.
        """

        if not self.legacy_news_and_event_tags.exists():
            return NewsAndEventsMixin(page=self).get_data()

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
class AccordionSnippet(index.Indexed, OptionalLink):
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

    search_fields = [
        index.SearchField("heading"),
        index.AutocompleteField("heading"),
        index.AutocompleteField("preview_text"),
        index.AutocompleteField("body"),
    ]


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
class ProgrammeSettings(BaseSiteSetting):
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
        super().save(*args, **kwargs)


@register_setting
class SitewideAlertSetting(BaseSiteSetting):
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
    slug = models.SlugField(blank=True, max_length=128)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


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
    contact_model_link_text = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional text for the linked url, form or email",
        verbose_name="Contact link text",
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
                FieldPanel("contact_model_link_text"),
                FieldPanel("contact_model_text"),
                FieldPanel("contact_model_form"),
                FieldPanel("contact_model_image"),
            ],
            "Contact",
        )
    ]


def get_listing_image(page):
    """Global function to get a page listing image, should use the
    listing_image if set, if not, check for a hero image

    Args:
        page: The page object

    Returns:
        rca.image.CustomImage / None: The image object
    """
    image = getattr(page, "listing_image")
    if not image:
        image = getattr(page, "hero_image", None)
    return image


class TapMixin(models.Model):
    tap_widget = models.ForeignKey(
        "utils.TapWidgetSnippet",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    panels = [FieldPanel("tap_widget")]

    class Meta:
        abstract = True


@register_snippet
class TapWidgetSnippet(models.Model):
    script_code = models.TextField(blank=True)
    admin_title = models.CharField(
        max_length=255,
        help_text="The title value is only used to identify the snippet in the admin interface ",
    )

    def __str__(self):
        return self.admin_title

    panels = [FieldPanel("admin_title"), FieldPanel("script_code")]


@register_setting
class SitewideTapSetting(BaseSiteSetting):
    class Meta:
        verbose_name = "Sitewide TAP settings"

    show_carousels = models.BooleanField(
        default=False, help_text="Checking this will show the site-wide TAP carousels"
    )

    show_widgets = models.BooleanField(
        default=False, help_text="Checking this will show the site-wide TAP widgets"
    )

    panels = [FieldPanel("show_carousels"), FieldPanel("show_widgets")]


@register_snippet
class CookieButtonSnippet(models.Model):
    title = models.CharField(max_length=255)
    panels = [
        FieldPanel("title", help_text="Required for internal purposes only"),
        HelpPanel(
            content=(
                "Only 1 snippet of this type can be created.<br>"
                "Use this snippet to place a button on the page that will "
                "allow the user to edit their cookie settings."
            )
        ),
    ]

    def __str__(self):
        return self.title

    def clean(self):
        if CookieButtonSnippet.objects.exists():
            raise ValidationError(
                {"title": ["Only one instance of CookieButtonSnippet is allowed."]}
            )


class StickyCTAMixin(models.Model):
    sticky_cta_description = models.TextField(verbose_name="Description", blank=True)
    sticky_cta_page = models.ForeignKey(
        "wagtailcore.Page",
        verbose_name="Page",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    sticky_cta_link_url = models.URLField(
        verbose_name="Link URL",
        blank=True,
    )
    sticky_cta_link_text = models.CharField(
        verbose_name="Link text",
        blank=True,
        max_length=255,
    )

    panels = MultiFieldPanel(
        [
            FieldPanel("sticky_cta_description"),
            FieldPanel("sticky_cta_page"),
            FieldPanel("sticky_cta_link_url"),
            FieldPanel("sticky_cta_link_text"),
        ],
        "Sticky Call To Action",
    )

    class Meta:
        abstract = True

    def full_clean(self, *args, **kwargs):
        super().full_clean(*args, **kwargs)

        errors = defaultdict(list)
        if self.sticky_cta_page and self.sticky_cta_link_url:
            message = "You must specify a page or link url. You can't use both."
            errors["sticky_cta_link_url"].append(message),
            errors["sticky_cta_page"].append(message),

        if bool(self.sticky_cta_link_url) != bool(self.sticky_cta_link_text):
            errors["sticky_cta_link_text"].append(
                "You must specify link text, if you use the link url field."
            )

        if self.sticky_cta_page or self.sticky_cta_link_url:
            # Either page or link URL is specified, so description is required
            if not self.sticky_cta_description:
                errors["sticky_cta_description"].append(
                    "You must specify a description for the sticky CTA"
                )

        if errors:
            raise ValidationError(errors)

    def get_sticky_cta(self):
        link = self.sticky_cta_link_url
        action = self.sticky_cta_link_text
        if page := self.sticky_cta_page:
            action = action or page.title
            link = page.url

        return {
            "message": self.sticky_cta_description,
            "action": action,
            "link": link,
            "modal": None,
        }
