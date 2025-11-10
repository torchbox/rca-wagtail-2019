from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from phonenumber_field.modelfields import PhoneNumberField
from wagtail.admin.panels import (
    FieldPanel,
    HelpPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
)
from wagtail.fields import RichTextField, StreamBlock, StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable, Page
from wagtail.search import index

from rca.editorial.models import EditorialPage
from rca.events.models import EventDetailPage
from rca.landingpages import admin_forms
from rca.landingpages.utils import (
    editorial_teaser_formatter,
    event_teaser_formatter,
    news_teaser_formatter,
)
from rca.navigation.models import LinkBlock as InternalExternalLinkBlock
from rca.projects.models import ProjectPage
from rca.utils.blocks import (
    CallToActionBlock,
    LinkBlock,
    LinkedImageBlock,
    RelatedPageListBlock,
    RelatedPageListBlockPage,
    SlideBlock,
    StatisticBlock,
)
from rca.utils.formatters import format_page_teasers
from rca.utils.models import (
    BasePage,
    ContactFieldsMixin,
    LegacyNewsAndEventsMixin,
    LinkFields,
    RelatedPage,
    TapMixin,
    get_listing_image,
)


class FeaturedImage(LinkFields):
    title = models.TextField(
        max_length=80,
        blank=True,
        help_text=_("The title has a maximum length of 80 characters"),
    )
    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    subtitle = models.TextField(
        max_length=120, blank=True, help_text=_("Maximum length of 120 characters")
    )
    description = models.TextField(
        max_length=250, blank=True, help_text=_("Maximum length of 250 characters")
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("image"),
        FieldPanel("subtitle"),
        FieldPanel("description"),
    ] + LinkFields.panels

    class Meta:
        abstract = True

    def clean(self):
        if self.link_page:
            if self.image or self.subtitle or self.description:
                raise ValidationError(
                    {
                        "link_page": ValidationError(
                            "Please remove the page link if you are are creating a custom teaser"
                        )
                    }
                )


class LandingPageStatsBlock(models.Model):
    source_page = ParentalKey("LandingPage", related_name="stats_block")
    title = models.CharField(
        max_length=125, help_text=_("Maximum length of 125 characters")
    )
    statistics = StreamField([("statistic", StatisticBlock())])
    background_image = models.ForeignKey(
        get_image_model_string(),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    page_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    panels = [
        FieldPanel("title"),
        FieldPanel("background_image"),
        FieldPanel("statistics"),
        FieldPanel("page_link"),
    ]

    def __str__(self):
        return self.title


class LandingPageFeaturedImage(FeaturedImage):
    source_page = ParentalKey("LandingPage", related_name="featured_image")


class LandingPageFeaturedImageSecondary(FeaturedImage):
    source_page = ParentalKey("LandingPage", related_name="featured_image_secondary")


class LandingPageRelatedPagegrid(RelatedPage):
    source_page = ParentalKey(
        "landingpages.LandingPage", related_name="related_pages_grid"
    )
    panels = [FieldPanel("page")]


class LandingPageRelatedPageHighlights(RelatedPage):
    source_page = ParentalKey(
        "landingpages.LandingPage", related_name="related_pages_highlights"
    )
    panels = [FieldPanel("page")]


class LandingPageRelatedPageSlide(RelatedPage):
    # For carousels and slideshows that now use page choosers and not URLs
    source_page = ParentalKey("landingpages.LandingPage", related_name="slideshow_page")
    panels = [PageChooserPanel("page", ["guides.GuidePage", "projects.ProjectPage"])]


class LandingPagePageSlideshowBlock(models.Model):
    source_page = ParentalKey("LandingPage", related_name="slideshow_block")
    title = models.CharField(
        max_length=125, help_text=_("Maximum length of 125 characters")
    )
    summary = models.CharField(
        max_length=250, blank=True, help_text=_("Maximum length of 250 characters")
    )
    slides = StreamField([("slide", SlideBlock())])
    panels = [FieldPanel("title"), FieldPanel("summary"), FieldPanel("slides")]

    def __str__(self):
        return self.title


class RelatedLandingPage(Orderable):
    source_page = ParentalKey(Page, related_name="related_landing_pages")
    page = models.ForeignKey("landingpages.LandingPage", on_delete=models.CASCADE)

    panels = [FieldPanel("page")]


class LandingPage(TapMixin, ContactFieldsMixin, LegacyNewsAndEventsMixin, BasePage):
    """Defines all the fields we will need for the other versions of landing pages
    visibility of some extra fields that aren't needed on certain models which inherit LandingPage
    are controlled at the content_panels level.

    There are two main reasons for this appoach:
    1. We don't need to create three times as many related models, the ParentalKeys can
        be "LandingPage" instead of ResearchLandingPage and InnovationLandingPage etc.
    2. The way data is shown in the templates is slightly different but the back end can
        be consistent, 'shaping' the page data can come from class methods on the main
        LandingPage class, or be overriden for the other LandingPage classes
    """

    template = "patterns/pages/landingpage/landing_page--generic.html"
    hero_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    introduction = models.TextField(
        max_length=500, blank=True, help_text=_("Maximum length of 500 characters")
    )
    about_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    highlights_title = models.TextField(
        max_length=80,
        blank=True,
        help_text=_("Maximum length of 80 characters"),
        verbose_name=_("Featured projects title"),
    )
    highlights_page_link_title = models.TextField(
        max_length=120,
        blank=True,
        help_text=_("The text do display for the link"),
        verbose_name=_("Featured projects link title"),
    )
    highlights_page_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Featured projects link"),
    )

    related_pages_title = models.TextField(
        max_length=80,
        blank=True,
        help_text=_(
            "The title to be displayed above the related pages grid, maximum length of 80 characters"
        ),
    )
    related_pages_text = models.TextField(
        max_length=250,
        blank=True,
        help_text=_(
            "The brief paragraph of text to be displayed above the related pages grid, maximum length of 80 characters"
        ),
    )
    page_list_title = models.TextField(
        max_length=80,
        blank=True,
        help_text=_(
            "The title to be displayed above the page list blocks, maximum length of 80 characters"
        ),
    )
    page_list = StreamField([("page_list", RelatedPageListBlock())], blank=True)
    cta_block = StreamField(
        [("call_to_action", CallToActionBlock(label=_("text promo")))],
        blank=True,
        verbose_name=_("Text promo"),
    )
    slideshow_title = models.CharField(
        max_length=125,
        help_text=_("Maximum length of 125 characters"),
        blank=True,
        verbose_name=_("Related content title"),
    )
    slideshow_summary = models.CharField(
        max_length=250,
        blank=True,
        help_text=_("Maximum length of 250 characters"),
        verbose_name=_("Related content summary"),
    )

    news_and_events_link_text = models.TextField(
        max_length=120,
        blank=True,
        help_text=_("The text to display for the 'View all news and events' link"),
    )
    news_and_events_link_target_url = models.URLField(
        blank=True, help_text="Add a link to view all news and events"
    )
    news_and_events_title = models.TextField(
        max_length=120,
        blank=True,
        help_text=_("The title to display above the news and events listing"),
    )

    search_fields = BasePage.search_fields + [
        index.SearchField("introduction"),
    ]

    content_panels = (
        BasePage.content_panels
        + [
            MultiFieldPanel(
                [FieldPanel("hero_image")],
                heading=_("Hero"),
            ),
            MultiFieldPanel(
                [FieldPanel("introduction"), FieldPanel("about_page")],
                heading=_("Introduction"),
            ),
            MultiFieldPanel(
                [
                    FieldPanel("highlights_title"),
                    InlinePanel("related_pages_highlights", label=_("Page"), max_num=8),
                    FieldPanel("highlights_page_link"),
                    FieldPanel("highlights_page_link_title"),
                ],
                heading=_("Featured projects"),
            ),
            MultiFieldPanel(
                [
                    FieldPanel("related_pages_title"),
                    FieldPanel("related_pages_text"),
                    InlinePanel(
                        "related_pages_grid", max_num=8, label=_("Related Pages")
                    ),
                ],
                heading=_("Related pages grid"),
            ),
            InlinePanel("featured_image", label=_("Featured content"), max_num=1),
            MultiFieldPanel(
                [
                    HelpPanel(
                        content=(
                            """<p>The title, link and link text displayed as part of the news and events
                        listing can be customised by adding overriding values here</p>"""
                        )
                    ),
                    FieldPanel("news_and_events_title"),
                    FieldPanel("news_and_events_link_text"),
                    FieldPanel("news_and_events_link_target_url"),
                    FieldPanel("legacy_news_and_event_tags"),
                ],
                "News and Events",
            ),
            MultiFieldPanel(
                [FieldPanel("page_list_title"), FieldPanel("page_list")],
                heading=_("Related page list"),
            ),
        ]
        + TapMixin.panels
    )

    @property
    def news_view_all(self):
        return {
            "link": self.news_and_events_link_target_url,
            "title": self.news_and_events_link_text,
        }

    def _format_projects_for_gallery(self, pages):
        """Internal method for formatting related projects to the correct
        structure for the gallery template"""
        items = []
        for page in pages[:8]:
            if page.page:
                related_page = page.page.specific
                meta = None
                items.append(
                    {
                        "title": related_page.title,
                        "link": related_page.url,
                        "image": related_page.hero_image,
                        "description": related_page.introduction,
                        "meta": meta,
                    }
                )
        return items

    def _format_featured_image(self, featured_image):
        # If a page object has been selected here, send
        # through the page object data rather than the manual fields
        if featured_image and featured_image.link_page:
            page = featured_image.link_page.specific
            image = page.listing_image
            introduction = page.listing_summary

            if hasattr(page, "hero_image"):
                image = page.hero_image
            if hasattr(page, "introduction"):
                introduction = page.introduction

            featured_image = {
                "title": featured_image.title,
                "subtitle": page.title,
                "description": introduction,
                "get_link_url": page.url,
                "image": image,
            }
        return featured_image

    def get_featured_image(self):
        if hasattr(self, "featured_image"):
            return self._format_featured_image(self.featured_image.first())

    def get_featured_image_secondary(self):
        if hasattr(self, "featured_image_secondary"):
            return self._format_featured_image(self.featured_image_secondary.first())

    def get_related_pages(self, pages):
        related_pages = []
        for value in pages.select_related("page"):
            if value.page and value.page.live:
                page = value.page.specific

                # different page types show different tags
                meta = None
                if hasattr(page, "related_school_pages"):
                    related_school = page.related_school_pages.first()
                    if related_school:
                        meta = related_school.page.title

                if isinstance(page, ProjectPage) and page.is_startup_project:
                    meta = "Start-up"

                related_pages.append(
                    {
                        "title": page.title,
                        "link": page.url,
                        "image": get_listing_image(page),
                        "description": (
                            page.introduction
                            if hasattr(page, "introduction")
                            else page.listing_summary
                        ),
                        "meta": meta,
                    }
                )
        return related_pages

    def get_page_list(self):
        """Formats the related items coming from streamfield blocks
        into a digestable list for the template"""
        items = []
        for block in self.page_list:
            # Page link can come from a page chooser, or a manual URL
            item = {
                "title": block.value["heading"],
                "related_items": [],
                "link": block.value["link"],
                "page_link": block.value["page_link"],
            }
            for page_block in block.value["page"]:
                if page_block.block_type == "custom_teaser":
                    page = {
                        "title": page_block.value["title"],
                        "url": page_block.value["link"]["url"],
                        "listing_image": page_block.value["image"],
                        "listing_summary": page_block.value["text"],
                        "meta": page_block.value["meta"],
                    }
                    item["related_items"].append(page)
                if page_block.block_type == "page":
                    if not page_block.value:
                        continue
                    item["related_items"].append(page_block.value.specific)
            items.append(item)
        return items

    def _format_slideshow_pages(self, slideshow_pages):
        slideshow = {
            "title": self.slideshow_title,
            "summary": self.slideshow_summary,
            "slides": [],
        }
        # The template is formatted to work with blocks, so we need to match the
        # data structure to now work with pages chooser values
        for slide in slideshow_pages.all():
            if not slide.page:
                continue

            page = slide.page.specific
            if not page.live:
                continue
            image = (
                page.hero_image if hasattr(page, "hero_image") else page.listing_image
            )
            summary = (
                page.introduction
                if hasattr(page, "introduction")
                else page.listing_summary
            )
            page_type = None
            page_type_mapping = {
                "GuidePage": "GUIDE",
                "ProjectPage": "PROJECT",
                "ResearchCentrePage": "RESEARCH CENTRE",
                "ShortCoursePage": "SHORT COURSE",
                "ProgrammePage": "PROGRAMME",
                "EventDetailPage": "EVENT",
                "SchoolPage": "SCHOOL",
            }
            # For editorial pages, use the type taxonomy as the meta value
            if hasattr(page, "editorial_types"):
                type = page.editorial_types.first()
                if type:
                    page_type_mapping["EditorialPage"] = type.type

            if page.__class__.__name__ in page_type_mapping:
                page_type = page_type_mapping[page.__class__.__name__]
            slideshow["slides"].append(
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
        return slideshow

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["about_page"] = self.about_page
        context["related_pages_highlights"] = self.get_related_pages(
            self.related_pages_highlights
        )
        context["related_pages"] = self.get_related_pages(self.related_pages_grid)
        context["featured_image"] = self.get_featured_image()
        context["page_list"] = self.get_page_list()
        context["stats_block"] = self.stats_block.select_related(
            "background_image"
        ).first()
        context["slideshow_block"] = self.slideshow_block.first()
        if self.tap_widget:
            context["tap_widget_code"] = mark_safe(self.tap_widget.script_code)
        return context


class ResearchLandingPage(LandingPage):
    template = "patterns/pages/landingpage/landing_page--research.html"

    content_panels = (
        BasePage.content_panels
        + [
            MultiFieldPanel(
                [FieldPanel("hero_image")],
                heading=_("Hero"),
            ),
            MultiFieldPanel(
                [FieldPanel("introduction"), FieldPanel("about_page")],
                heading=_("Introduction"),
            ),
            MultiFieldPanel(
                [
                    FieldPanel("highlights_title"),
                    InlinePanel("related_pages_highlights", label=_("Page"), max_num=8),
                    FieldPanel("highlights_page_link"),
                    FieldPanel("highlights_page_link_title"),
                ],
                heading=_("Featured projects"),
            ),
            MultiFieldPanel(
                [
                    HelpPanel(
                        content=(
                            """<p>The title, link and link text displayed as part of the news and events
                            listing can be customised by adding overriding values here</p>"""
                        )
                    ),
                    FieldPanel("news_and_events_title"),
                    FieldPanel("news_and_events_link_text"),
                    FieldPanel("news_and_events_link_target_url"),
                    FieldPanel("legacy_news_and_event_tags"),
                ],
                "News and Events",
            ),
            MultiFieldPanel(
                [FieldPanel("page_list_title"), FieldPanel("page_list")],
                heading=_("Related page list"),
            ),
            InlinePanel("featured_image", label=_("Featured content"), max_num=1),
            MultiFieldPanel(
                [
                    FieldPanel("slideshow_title"),
                    FieldPanel("slideshow_summary"),
                    InlinePanel("slideshow_page", label=_("Page")),
                ],
                heading=_("Related content"),
            ),
            FieldPanel("cta_block"),
            MultiFieldPanel(
                [
                    FieldPanel("contact_model_image"),
                    FieldPanel("contact_model_title"),
                    FieldPanel("contact_model_text"),
                    FieldPanel("contact_model_email"),
                    FieldPanel("contact_model_url"),
                    FieldPanel("contact_model_form"),
                ],
                heading="Contact information",
            ),
        ]
        + TapMixin.panels
    )

    class Meta:
        verbose_name = "Landing Page - Research"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # reset the slideshow block so it can be re-populated as it's set in
        # the parent context for other slideshow formats.
        context["slideshow_block"] = []
        if self.tap_widget:
            context["tap_widget_code"] = mark_safe(self.tap_widget.script_code)
        if self.slideshow_page.first():
            context["slideshow_block"] = self._format_slideshow_pages(
                self.slideshow_page.all()
            )
        return context


class InnovationLandingPage(LandingPage):
    template = "patterns/pages/landingpage/landing_page--innovation.html"

    content_panels = (
        BasePage.content_panels
        + [
            MultiFieldPanel(
                [FieldPanel("hero_image")],
                heading=_("Hero"),
            ),
            MultiFieldPanel(
                [FieldPanel("introduction"), FieldPanel("about_page")],
                heading=_("Introduction"),
            ),
            MultiFieldPanel(
                [InlinePanel("featured_image", label=_("Featured image"), max_num=1)],
                heading=_("Featured content - top"),
            ),
            MultiFieldPanel(
                [
                    HelpPanel(
                        content=(
                            """<p>The title, link and link text displayed as part of the news and events
                            listing can be customised by adding overriding values here</p>"""
                        )
                    ),
                    FieldPanel("news_and_events_title"),
                    FieldPanel("news_and_events_link_text"),
                    FieldPanel("news_and_events_link_target_url"),
                    FieldPanel("legacy_news_and_event_tags"),
                ],
                "News and Events",
            ),
            MultiFieldPanel(
                [FieldPanel("page_list_title"), FieldPanel("page_list")],
                heading=_("Related page list"),
            ),
            InlinePanel("stats_block", label="Statistics", max_num=1),
            MultiFieldPanel(
                [
                    FieldPanel("highlights_title"),
                    InlinePanel("related_pages_highlights", label=_("Page"), max_num=8),
                    FieldPanel("highlights_page_link"),
                    FieldPanel("highlights_page_link_title"),
                ],
                heading=_("Featured projects"),
            ),
            MultiFieldPanel(
                [
                    InlinePanel(
                        "featured_image_secondary", label=_("Featured image"), max_num=1
                    )
                ],
                heading=_("Featured content - bottom"),
            ),
            MultiFieldPanel(
                [
                    FieldPanel("contact_model_image"),
                    FieldPanel("contact_model_title"),
                    FieldPanel("contact_model_text"),
                    FieldPanel("contact_model_email"),
                    FieldPanel("contact_model_url"),
                    FieldPanel("contact_model_form"),
                ],
                heading="Contact information",
            ),
        ]
        + TapMixin.panels
    )

    class Meta:
        verbose_name = "Landing Page - Innovation"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["featured_image_secondary"] = self.get_featured_image_secondary()
        context["page_list"] = self.get_page_list()
        if self.tap_widget:
            context["tap_widget_code"] = mark_safe(self.tap_widget.script_code)
        return context


class EnterpriseLandingPage(LandingPage):
    template = "patterns/pages/landingpage/landing_page--enterprise.html"

    content_panels = LandingPage.content_panels

    class Meta:
        verbose_name = "Landing Page - Enterprise"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        if self.tap_widget:
            context["tap_widget_code"] = mark_safe(self.tap_widget.script_code)
        return context


class EELandingPageRelatedEditorialPage(RelatedPage):
    source_page = ParentalKey(
        "landingpages.EELandingPage", related_name="related_editorial_pages"
    )
    panels = [PageChooserPanel("page", ["editorial.EditorialPage"])]


class EELandingPageRelatedEditorialStoryPage(RelatedPage):
    source_page = ParentalKey(
        "landingpages.EELandingPage", related_name="related_editorial_story_pages"
    )
    panels = [PageChooserPanel("page", ["editorial.EditorialPage"])]


class EELandingPageRelatedEventPage(RelatedPage):
    source_page = ParentalKey(
        "landingpages.EELandingPage", related_name="related_event_pages"
    )
    panels = [PageChooserPanel("page", ["events.EventDetailPage"])]


class EELandingPage(ContactFieldsMixin, BasePage):
    base_form_class = admin_forms.LandingPageAdminForm
    template = "patterns/pages/editorial_event_landing/editorial_event_landing.html"
    max_count = 1

    news_link_text = models.TextField(
        max_length=120,
        blank=False,
        help_text=_("The text do display for the link"),
    )
    news_link_target_url = models.URLField(blank=False)

    events_link_text = models.TextField(
        max_length=120,
        blank=False,
        help_text=_("The text do display for the link"),
    )
    events_link_target_url = models.URLField(blank=False)

    stories_summary_text = models.TextField(
        max_length=250,
        blank=False,
        help_text=_("Short text summary displayed with the 'Stories' title"),
    )
    stories_link_text = models.TextField(
        max_length=120,
        blank=False,
        help_text=_("The text do display for the link"),
    )
    stories_link_target_url = models.URLField(blank=False)

    podcasts_summary_text = models.TextField(
        max_length=250,
        blank=False,
        help_text=_("Short text summary displayed with the 'Podcasts' title"),
    )
    podcasts_link_text = models.TextField(
        max_length=120,
        blank=False,
        help_text=_("The text do display for the link"),
    )
    podcasts_link_target_url = models.URLField(blank=False)
    podcasts_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    video_caption = models.CharField(
        blank=True,
        max_length=80,
        help_text=_("The text displayed next to the video play button"),
    )
    video = models.URLField(blank=True)
    cta_navigation_title = models.CharField(
        max_length=80,
        help_text=_("The text displayed for this section in the in-page navigation"),
    )
    cta_block = StreamField(
        StreamBlock(
            [("call_to_action", CallToActionBlock())],
            max_num=1,
        ),
        blank=True,
    )

    class Meta:
        verbose_name = "Landing Page - Editorial and Events"

    def featured_news(self):
        news = []
        picked_news = self.related_editorial_pages.first()
        if picked_news:
            picked_news = picked_news.page.specific
            news.append(news_teaser_formatter(picked_news, return_image=True))

        # Get 3 more items
        latest_news_items = (
            EditorialPage.objects.live()
            .filter(show_on_landing_page=True)
            .order_by("-published_at")
            .exclude(id=picked_news.id)
            .prefetch_related("hero_image", "editorial_types")[:3]
        )
        for item in latest_news_items:
            news.append(news_teaser_formatter(item))

        return news

    def featured_events(self):
        events = []
        picked_event = self.related_event_pages.first()
        if picked_event:
            picked_event = picked_event.page.specific
            events.append(event_teaser_formatter(picked_event, return_image=True))

        # Get 3 more items
        latest_event_items = (
            EventDetailPage.objects.live()
            .filter(start_date__gte=timezone.now().date())
            .exclude(id=picked_event.id)
            .order_by("start_date")
            .prefetch_related("hero_image")[:3]
        )
        for item in latest_event_items:
            events.append(event_teaser_formatter(item))

        return events

    def get_stories(self):
        pages = self.related_editorial_story_pages.all().select_related("page")
        return [
            editorial_teaser_formatter(page.page.specific)
            for page in pages
            if page.page
        ]

    @property
    def news_view_all(self):
        return {"link": self.news_link_target_url, "title": self.news_link_text}

    @property
    def events_view_all(self):
        return {"link": self.events_link_target_url, "title": self.events_link_text}

    def custom_anchor_heading_item(self):
        # The cta_block acts as an extra heading for the navigation, and there
        # Can only be one, so return it in the style of the anchor nav
        if self.cta_block:
            for block in self.cta_block:
                return {
                    "title": self.cta_navigation_title,
                    "link": slugify(self.cta_navigation_title),
                }

    def anchor_nav(self):
        """Build list of data to be used as
        in-page navigation"""
        return [
            {"title": "News", "link": "news"},
            {"title": "Events", "link": "events"},
            {"title": "Stories", "link": "stories"},
            {"title": "Podcasts", "link": "podcasts"},
            {
                "title": self.cta_navigation_title,
                "link": slugify(self.cta_navigation_title),
            },
        ]

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                InlinePanel(
                    "related_editorial_pages",
                    max_num=1,
                    min_num=1,
                    label="Editorial Page",
                ),
                FieldPanel("news_link_text"),
                FieldPanel("news_link_target_url"),
            ],
            heading="Featured News",
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    "related_event_pages", max_num=1, min_num=1, label="Event Page"
                ),
                FieldPanel("events_link_text"),
                FieldPanel("events_link_target_url"),
            ],
            heading="Featured Events",
        ),
        MultiFieldPanel(
            [
                FieldPanel("stories_summary_text"),
                FieldPanel("stories_link_text"),
                FieldPanel("stories_link_target_url"),
                InlinePanel(
                    "related_editorial_story_pages", label="Editorial Page", max_num=6
                ),
            ],
            heading="Stories",
        ),
        MultiFieldPanel(
            [
                FieldPanel("podcasts_summary_text", heading="Summary text"),
                FieldPanel("podcasts_image", heading="Image"),
                FieldPanel("video_caption"),
                FieldPanel("video"),
                FieldPanel("podcasts_link_text", heading="Podcasts link text"),
                FieldPanel(
                    "podcasts_link_target_url", heading="Podcasts link target URL"
                ),
            ],
            heading="Podcasts",
        ),
        MultiFieldPanel(
            [FieldPanel("cta_navigation_title"), FieldPanel("cta_block")],
            heading="CTA",
        ),
        MultiFieldPanel(
            [
                FieldPanel("contact_model_title"),
                FieldPanel("contact_model_email"),
                FieldPanel("contact_model_url"),
                FieldPanel("contact_model_form"),
                FieldPanel("contact_model_link_text"),
                FieldPanel("contact_model_text"),
                FieldPanel("contact_model_image"),
            ],
            "Large Call To Action",
        ),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["news"] = self.featured_news()
        context["events"] = self.featured_events()
        context["stories"] = self.get_stories()
        context["tabs"] = self.anchor_nav()
        context["custom_tab_heading"] = self.custom_anchor_heading_item()
        return context


class AlumniLandingPageRelatedEditorialPage(RelatedPage):
    source_page = ParentalKey(
        "landingpages.AlumniLandingPage", related_name="related_editorial_pages"
    )
    panels = [PageChooserPanel("page", ["editorial.EditorialPage"])]


class AlumniLandingPageSecondaryRelatedEditorialPage(RelatedPage):
    source_page = ParentalKey(
        "landingpages.AlumniLandingPage",
        related_name="related_editorial_pages_secondary",
    )
    panels = [PageChooserPanel("page", ["editorial.EditorialPage"])]


class AlumniLandingPageRelatedPageSlide(RelatedPage):
    source_page = ParentalKey(
        "landingpages.LandingPage", related_name="alumni_slideshow_page"
    )
    panels = [FieldPanel("page")]


class AlumniLandingPageTeaser(models.Model):
    source_page = ParentalKey("AlumniLandingPage", related_name="page_teasers")
    title = models.CharField(max_length=125)
    summary = models.CharField(max_length=250, blank=True)
    pages = StreamField(
        StreamBlock([("Page", RelatedPageListBlockPage(max_num=6))], max_num=1),
    )
    panels = [FieldPanel("title"), FieldPanel("summary"), FieldPanel("pages")]

    def __str__(self):
        return self.title


class AlumniLandingPage(LandingPage):
    max_count = 1
    base_form_class = admin_forms.LandingPageAdminForm
    template = "patterns/pages/alumni/alumni.html"
    location = RichTextField(blank=True, features=(["bold", "italic"]))
    social_links = StreamField(
        StreamBlock([("Link", LinkBlock())], max_num=5), blank=True
    )
    contact_email = models.EmailField(blank=True, max_length=254)
    body = RichTextField(blank=True)
    video_caption = models.CharField(
        blank=True,
        max_length=80,
        help_text=_("The text displayed next to the video play button"),
    )
    video = models.URLField(blank=True)
    video_preview_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    # get involved section
    collaborators_heading = models.CharField(
        blank=True,
        max_length=80,
        help_text=_("The text displayed above the collaborators carousel"),
    )
    collaborators = StreamField(
        StreamBlock([("Collaborator", LinkedImageBlock())], max_num=9, required=False),
        blank=True,
        help_text="You can add up to 9 collaborators. Minimum 200 x 200 pixels. \
            Aim for logos that sit on either a white or transparent background.",
    )
    # "latest"' section
    news_link_text = models.TextField(
        max_length=120,
        blank=False,
        help_text=_("The text do display for the link"),
    )
    news_link_target_url = models.URLField(blank=False)
    latest_intro = models.CharField(
        max_length=250,
        blank=True,
        help_text=_("Optional short text summary for the 'Latest' section"),
        verbose_name="Latest section summary",
    )
    additional_links = StreamField(
        [("link", InternalExternalLinkBlock())],
        blank=True,
        verbose_name="Additional Links",
    )
    latest_cta_block = StreamField(
        [("call_to_action", CallToActionBlock(label=_("text promo")))],
        blank=True,
        verbose_name=_("Text promo"),
    )

    content_panels = (
        BasePage.content_panels
        + [
            MultiFieldPanel(
                [FieldPanel("hero_image")],
                heading=_("Hero"),
            ),
            FieldPanel("introduction"),
            MultiFieldPanel(
                [
                    FieldPanel("video"),
                    FieldPanel("video_caption"),
                    FieldPanel("video_preview_image"),
                ],
                heading="Video",
            ),
            FieldPanel("body"),
            InlinePanel("page_teasers", max_num=1, label="Page teasers"),
            # latest
            FieldPanel("latest_intro"),
            MultiFieldPanel(
                [
                    InlinePanel(
                        "related_editorial_pages",
                        heading="Related Alumni Editorial 'news' pages",
                        max_num=3,
                    ),
                    FieldPanel("news_link_target_url"),
                    FieldPanel("news_link_text"),
                ],
                heading="Related news",
            ),
            InlinePanel(
                "related_editorial_pages_secondary",
                heading="Related Alumni Editorial 'story' pages",
                max_num=6,
            ),
            FieldPanel("additional_links"),
            FieldPanel("latest_cta_block"),
            # Get involved
            MultiFieldPanel(
                [
                    FieldPanel("slideshow_summary"),
                    InlinePanel("alumni_slideshow_page", label=_("Page")),
                ],
                heading=_("'Get invoved' slideshow"),
            ),
            MultiFieldPanel(
                [FieldPanel("collaborators_heading"), FieldPanel("collaborators")],
                heading="Collaborators",
            ),
            FieldPanel("cta_block"),
            InlinePanel("stats_block", label="Statistics", max_num=1),
            MultiFieldPanel(
                [
                    FieldPanel("contact_model_title"),
                    FieldPanel("contact_model_email"),
                    FieldPanel("contact_model_url"),
                    FieldPanel("contact_model_form"),
                    FieldPanel("contact_model_link_text"),
                    FieldPanel("contact_model_text"),
                    FieldPanel("contact_model_image"),
                ],
                "Contact information",
            ),
        ]
        + TapMixin.panels
    )

    key_details_panels = [
        FieldPanel("location"),
        FieldPanel("contact_email"),
        MultiFieldPanel(
            [FieldPanel("social_links")], heading="Social media profile links"
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )

    @property
    def news_view_all(self):
        return {"link": self.news_link_target_url, "title": self.news_link_text}

    def get_related_editorial_pages(self, pages):
        related_pages = []
        for value in pages.select_related("page"):
            if value.page and value.page.live:
                page = value.page.specific
                related_pages.append(news_teaser_formatter(page, True))
        return related_pages

    def anchor_nav(self):
        """Build list of data to be used as
        in-page navigation"""
        return [
            {"title": "Alumni benefits", "link": "alumni-benefits"},
            {"title": "Latest", "link": "latest"},
            {"title": "Get involved", "link": "get-involved"},
            {"title": "Stay connected", "link": "stay-connected"},
        ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["related_editorial_news"] = self.get_related_editorial_pages(
            self.related_editorial_pages
        )
        context["editorial_stories"] = []
        if self.related_editorial_pages_secondary.first():
            context["editorial_stories"] = self._format_slideshow_pages(
                self.related_editorial_pages_secondary.all()
            )
        context["get_involved"] = self._format_slideshow_pages(
            self.alumni_slideshow_page.all()
        )
        context["page_teasers"] = format_page_teasers(self.page_teasers.first())
        context["tabs"] = self.anchor_nav()
        return context


class DevelopmentLandingPageRelatedPage(RelatedPage):
    source_page = ParentalKey(
        "landingpages.DevelopmentLandingPage", related_name="related_help_pages"
    )
    panels = [FieldPanel("page")]


class DevelopmentLandingPageRelatedEditorialPage(RelatedPage):
    source_page = ParentalKey(
        "landingpages.DevelopmentLandingPage", related_name="related_editorial_pages"
    )
    panels = [PageChooserPanel("page", ["editorial.EditorialPage"])]


class DevelopmentLandingPage(LandingPage):
    max_count = 1
    base_form_class = admin_forms.LandingPageAdminForm
    template = "patterns/pages/development/development.html"
    location = RichTextField(blank=True, features=(["bold", "italic"]))
    contact_tel = PhoneNumberField(blank=True)
    contact_tel_display_text = models.CharField(
        max_length=120,
        help_text=(
            "Specify specific text or numbers to display for the linked tel "
            "number, e.g. +44 (0)20 7590 1234 or +44 (0)7749 183783"
        ),
        blank=True,
    )
    contact_email = models.EmailField(blank=True, max_length=254)
    social_links = StreamField(
        StreamBlock([("Link", LinkBlock())], max_num=5), blank=True
    )
    video_caption = models.CharField(
        blank=True,
        max_length=80,
        help_text=_("The text displayed next to the video play button"),
    )
    video = models.URLField(blank=True)
    video_preview_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = RichTextField(blank=True)
    how_you_can_help_intro = models.CharField(
        max_length=250,
        blank=True,
        help_text=_("Short text summary for the section"),
    )
    help_cta_block = StreamField(
        [("call_to_action", CallToActionBlock(label=_("text promo")))],
        blank=True,
        verbose_name=_("Text promo"),
    )
    # "Stories"' section
    stories_link_text = models.TextField(
        max_length=120,
        blank=False,
        help_text=_("The text do display for the link"),
    )
    stories_link_target_url = models.URLField(blank=False)
    stories_intro = models.CharField(
        max_length=250,
        blank=True,
        help_text=_("Optional short text summary for the 'Stories' section"),
        verbose_name="Stories section summary",
    )
    stories_cta_block = StreamField(
        [("call_to_action", CallToActionBlock(label=_("text promo")))],
        blank=True,
        verbose_name=_("Text promo"),
    )

    content_panels = (
        BasePage.content_panels
        + [
            MultiFieldPanel(
                [FieldPanel("hero_image")],
                heading=_("Hero"),
            ),
            FieldPanel("introduction"),
            MultiFieldPanel(
                [
                    FieldPanel("video"),
                    FieldPanel("video_caption"),
                    FieldPanel("video_preview_image"),
                ],
                heading="Video",
            ),
            FieldPanel("body"),
            MultiFieldPanel(
                [
                    FieldPanel("related_pages_text"),
                    InlinePanel(
                        "related_pages_grid", max_num=5, label=_("Related Pages")
                    ),
                ],
                heading=_("Related pages grid"),
            ),
            FieldPanel("cta_block"),
            InlinePanel("stats_block", label="Statistics", max_num=1),
            MultiFieldPanel(
                [
                    FieldPanel("how_you_can_help_intro"),
                    InlinePanel("related_help_pages", label="Page", max_num=6),
                    FieldPanel("help_cta_block"),
                ],
                heading="How you can help",
            ),
            MultiFieldPanel(
                [
                    FieldPanel("stories_intro"),
                    InlinePanel(
                        "related_editorial_pages",
                        heading="Related Editorial pages",
                        label="Editorial page",
                        max_num=3,
                    ),
                    FieldPanel("stories_link_text"),
                    FieldPanel("stories_link_target_url"),
                    FieldPanel("stories_cta_block"),
                ],
                heading="Success stories",
            ),
            MultiFieldPanel(
                [
                    FieldPanel("contact_model_title"),
                    FieldPanel("contact_model_email"),
                    FieldPanel("contact_model_url"),
                    FieldPanel("contact_model_form"),
                    FieldPanel("contact_model_link_text"),
                    FieldPanel("contact_model_text"),
                    FieldPanel("contact_model_image"),
                ],
                "Contact information",
            ),
        ]
        + TapMixin.panels
    )

    key_details_panels = [
        FieldPanel("location"),
        MultiFieldPanel(
            [
                FieldPanel("contact_tel"),
                FieldPanel("contact_tel_display_text"),
                FieldPanel("contact_email"),
            ],
            heading="Get in touch",
        ),
        MultiFieldPanel(
            [FieldPanel("social_links")], heading="Social media profile links"
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )

    def get_related_editorial_pages(self, pages):
        related_pages = []
        for value in pages.select_related("page"):
            if value.page and value.page.live:
                page = value.page.specific
                related_pages.append(news_teaser_formatter(page, True))
        return related_pages

    def anchor_nav(self):
        """Build list of data to be used as
        in-page navigation"""
        return [
            {"title": "The story", "link": "the-story"},
            {"title": "How you can help", "link": "how-you-can-help"},
            {"title": "Success stories", "link": "success-stories"},
            {"title": "Contact", "link": "contact"},
        ]

    @property
    def stories_view_all(self):
        return {"link": self.stories_link_target_url, "title": self.stories_link_text}

    def get_related_help_pages(self):
        pages = self.related_help_pages.all().select_related("page")
        return [editorial_teaser_formatter(page.page.specific) for page in pages]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["tabs"] = self.anchor_nav()
        context["page_teasers"] = self.get_related_pages(self.related_pages_grid)
        context["help_pages"] = self.get_related_pages(self.related_help_pages)
        context["stories"] = self.get_related_editorial_pages(
            self.related_editorial_pages
        )
        return context


class TapLandingPage(LandingPage):
    template = "patterns/pages/landingpage/landing_page--tap.html"
    tap_carousel = models.TextField(blank=True, verbose_name="Iframe Code")

    class Meta:
        verbose_name = "Landing Page - TAP"

    content_panels = (
        BasePage.content_panels
        + [
            MultiFieldPanel(
                [FieldPanel("hero_image")],
                heading=_("Hero"),
            ),
            MultiFieldPanel(
                [FieldPanel("introduction"), FieldPanel("about_page")],
                heading=_("Introduction"),
            ),
            MultiFieldPanel([FieldPanel("tap_carousel")], heading="TAP Carousel"),
            MultiFieldPanel(
                [
                    FieldPanel("highlights_title"),
                    InlinePanel("related_pages_highlights", label=_("Page"), max_num=8),
                    FieldPanel("highlights_page_link"),
                    FieldPanel("highlights_page_link_title"),
                ],
                heading=_("Featured projects"),
            ),
            MultiFieldPanel(
                [
                    FieldPanel("related_pages_title"),
                    FieldPanel("related_pages_text"),
                    InlinePanel(
                        "related_pages_grid", max_num=8, label=_("Related Pages")
                    ),
                ],
                heading=_("Related pages grid"),
            ),
            InlinePanel("featured_image", label=_("Featured content"), max_num=1),
            MultiFieldPanel(
                [
                    HelpPanel(
                        content=(
                            """<p>The title, link and link text displayed as part of the news and events
                        listing can be customised by adding overriding values here</p>"""
                        )
                    ),
                    FieldPanel("news_and_events_title"),
                    FieldPanel("news_and_events_link_text"),
                    FieldPanel("news_and_events_link_target_url"),
                    FieldPanel("legacy_news_and_event_tags"),
                ],
                "News and Events",
            ),
            MultiFieldPanel(
                [FieldPanel("page_list_title"), FieldPanel("page_list")],
                heading=_("Related page list"),
            ),
        ]
        + TapMixin.panels
    )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["tap_carousel"] = mark_safe(self.tap_carousel)
        return context
