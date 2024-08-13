from collections import defaultdict
from itertools import chain

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, HelpPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import StreamBlock, StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable

from rca.api_content.content import get_alumni_stories as get_api_alumni_stories
from rca.api_content.content import get_news_and_events as get_api_news_and_events
from rca.editorial.models import EditorialPage
from rca.events.models import EventDetailPage
from rca.utils.blocks import RelatedPageListBlockPage, StatisticBlock
from rca.utils.models import (
    DARK_HERO,
    DARK_TEXT_ON_LIGHT_IMAGE,
    HERO_COLOUR_CHOICES,
    LIGHT_HERO,
    BasePage,
    TapMixin,
    get_listing_image,
)


class HomePageTransofmrationBlock(models.Model):
    source_page = ParentalKey("HomePage", related_name="transformation_blocks")
    heading = models.CharField(
        max_length=125, help_text="Large heading displayed above the image"
    )
    image = models.ForeignKey(
        get_image_model_string(),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    video = models.URLField(blank=True)
    video_caption = models.CharField(
        blank=True,
        max_length=80,
        help_text="The text displayed next to the video play button",
    )
    sub_heading = models.CharField(
        max_length=125, blank=True, help_text="The title below the image"
    )
    page_title = models.CharField(
        max_length=125,
        blank=True,
        help_text="Please add informative help text that includes the name or nature of the target content",
    )
    page_summary = models.CharField(
        max_length=250, blank=True, help_text="A summary for the linked related page"
    )
    page_link_url = models.URLField(blank=True, help_text="A url to a related page")
    read_more_link_text = models.CharField(
        max_length=125,
        blank=True,
        help_text="Specific text to use for the 'read more' link",
    )

    panels = [
        FieldPanel("heading"),
        FieldPanel("image"),
        FieldPanel("video"),
        FieldPanel("video_caption"),
        FieldPanel("sub_heading"),
        FieldPanel("page_title"),
        FieldPanel("page_summary"),
        FieldPanel("page_link_url"),
        FieldPanel("read_more_link_text"),
    ]

    def __str__(self):
        return self.heading

    def clean(self):
        errors = defaultdict(list)
        if self.video and not self.video_caption:
            errors["video_caption"].append("Please add a caption for the video")

        if errors:
            raise ValidationError(errors)


class HomePagePartnershipBlock(models.Model):
    # Partnership module
    source_page = ParentalKey("HomePage", related_name="partnerships_block")
    title = models.CharField(max_length=125)
    summary = models.CharField(max_length=250)
    slides = StreamField(
        StreamBlock([("Page", RelatedPageListBlockPage())], max_num=1),
    )

    panels = [FieldPanel("title"), FieldPanel("summary"), FieldPanel("slides")]

    def __str__(self):
        return self.title


class HomePageStatsBlock(models.Model):
    source_page = ParentalKey("HomePage", related_name="stats_block")
    title = models.CharField(max_length=125)
    statistics = StreamField([("statistic", StatisticBlock())])
    background_image = models.ForeignKey(
        get_image_model_string(),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    panels = [
        FieldPanel("title"),
        FieldPanel("background_image"),
        FieldPanel("statistics"),
    ]

    def __str__(self):
        return self.title


class HomePageFeaturedAlumniStory(Orderable):
    source_page = ParentalKey("HomePage", related_name="featured_alumni_stories")
    story = models.ForeignKey("editorial.EditorialPage", on_delete=models.CASCADE)


class HomePage(TapMixin, BasePage):
    template = "patterns/pages/home/home_page.html"

    # Only allow creating HomePages at the root level
    parent_page_types = ["wagtailcore.Page"]

    hero_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_colour_option = models.PositiveSmallIntegerField(choices=(HERO_COLOUR_CHOICES))
    hero_cta_url = models.URLField(blank=True)
    hero_image_credit = models.CharField(
        max_length=255,
        blank=True,
        help_text="Adding specific credit text here will \
        override the images meta data fields.",
    )
    hero_cta_text = models.CharField(max_length=125, blank=True)
    hero_cta_sub_text = models.CharField(max_length=125, blank=True)

    strapline = models.CharField(max_length=125)
    strapline_cta_url = models.URLField(blank=True)
    strapline_cta_text = models.CharField(max_length=125, blank=True)

    use_api_for_alumni_stories = models.BooleanField(default=True)
    use_api_for_news_and_events = models.BooleanField(default=True)
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
    content_panels = (
        BasePage.content_panels
        + [
            MultiFieldPanel(
                [
                    FieldPanel("hero_image"),
                    FieldPanel("hero_image_credit"),
                    FieldPanel("hero_colour_option"),
                    FieldPanel("hero_cta_url"),
                    FieldPanel("hero_cta_text"),
                    FieldPanel("hero_cta_sub_text"),
                ],
                heading="Hero",
            ),
            MultiFieldPanel(
                [
                    FieldPanel("strapline"),
                    FieldPanel("strapline_cta_url"),
                    FieldPanel("strapline_cta_text"),
                ],
                heading="Strapline",
            ),
            InlinePanel(
                "featured_alumni_stories",
                label="Story",
                heading="Featured Alumni stories",
            ),
            InlinePanel(
                "transformation_blocks", label="Transformation block", max_num=1
            ),
            InlinePanel("partnerships_block", label="Partnerships", max_num=1),
            InlinePanel("stats_block", label="Statistics", max_num=1),
            MultiFieldPanel(
                [
                    HelpPanel(
                        content=(
                            """<p>These fields control if news/events/alumni stories are fetched
                        from the legacy website.</p>
                        <p>If un-checked, the content featured here will use pages created on
                        <strong>this</strong> site:</p>
                        <ul>
                        <li>editorial pages tagged with 'news' or 'alumni story'</li>
                        <li>'EventPages' with a start date closest to today</li>
                        </ul>"""
                        )
                    ),
                    FieldPanel("use_api_for_alumni_stories"),
                    FieldPanel("use_api_for_news_and_events"),
                ],
                heading="News, Events and Alumni Stories Content Listings",
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
                ],
                "News and Events",
            ),
        ]
        + TapMixin.panels
    )

    def clean(self):
        errors = defaultdict(list)
        if self.hero_cta_url and not self.hero_cta_text:
            errors["hero_cta_text"].append(
                "Please add the text to be displayed as a link"
            )
        if self.hero_cta_text and not self.hero_cta_url:
            errors["hero_cta_url"].append("Please add a URL value")
        if self.strapline_cta_url and not self.strapline_cta_text:
            errors["hero_cta_text"].append(
                "Please add the text to be displayed as a link"
            )
        if self.strapline_cta_text and not self.strapline_cta_url:
            errors["hero_cta_url"].append("Please add a URL value")

        if errors:
            raise ValidationError(errors)

    @property
    def news_view_all(self):
        return {
            "link": self.news_and_events_link_target_url,
            "title": self.news_and_events_link_text,
        }

    def _format_partnerships(self, partnerships_block):
        # The partnerships.slides field offers choice between a page
        # or a custom teaser, this method formats the data so either values
        # can be sent to the homepage template and format into a slideshow
        if not partnerships_block:
            return
        slideshow = {
            "title": partnerships_block.title,
            "summary": partnerships_block.summary,
            "slides": [],
        }
        for slide in partnerships_block.slides:
            for block in slide.value:
                if block.block_type == "custom_teaser":
                    slideshow["slides"].append(
                        {
                            "value": {
                                "title": block.value["title"],
                                "summary": block.value["text"],
                                "image": block.value["image"],
                                "link": block.value["link"]["url"],
                                "type": block.value["meta"],
                            }
                        }
                    )
                elif block.block_type == "page":
                    page_type = None
                    page_type_mapping = {
                        "GuidePage": "GUIDE",
                        "ProjectPage": "PROJECT",
                        "ResearchCentrePage": "RESEARCH CENTRE",
                        "ShortCoursePage": "SHORT COURSE",
                        "ProgrammePage": "PROGRAMME",
                    }
                    page = block.value.specific

                    if page.__class__.__name__ in page_type_mapping:
                        page_type = page_type_mapping.get(page.__class__.__name__, None)
                    summary = (
                        page.introduction
                        if hasattr(page, "introduction")
                        else page.listing_summary
                    )
                    image = (
                        page.hero_image
                        if hasattr(page, "hero_image")
                        else page.listing_image
                    )
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

    def related_news_events_formatter(
        self, page, long_description=False, editorial_meta_label=""
    ):
        # Organsises data into a digestable format for the template.
        editorial_meta = editorial_meta_label
        PAGE_META_MAPPING = {
            "EditorialPage": editorial_meta,
            "EventDetailPage": "Event",
        }
        editorial_published_date = getattr(page, "published_at", None)
        if editorial_published_date and not long_description:
            editorial_description = editorial_published_date.strftime("%-d %B %Y")
        else:
            editorial_description = page.introduction

        PAGE_DESCRIPTION_MAPPING = {
            "EditorialPage": editorial_description,
            "EventDetailPage": getattr(page, "event_date_short", None),
        }
        meta = PAGE_META_MAPPING.get(page.__class__.__name__, "")
        description = PAGE_DESCRIPTION_MAPPING.get(page.__class__.__name__, "")
        try:
            image = get_listing_image(page).get_rendition("fill-878x472").url
        except AttributeError:
            image = None
        return {
            "image": image,
            "title": page.title,
            "link": page.url,
            "description": description,
            "type": meta,
        }

    def get_news_and_events(self):
        if self.use_api_for_news_and_events:
            return get_api_news_and_events()

        # Try and find an upcoming event
        event = (
            EventDetailPage.objects.live()
            .filter(start_date__gte=timezone.now().date())
            .order_by("start_date")[:1]
        )

        # If there is an event, we'll show 2 news items and 1 event
        NEWS_ITEMS = 2 if event else 3

        # get NEWS_ITEMS
        news = (
            EditorialPage.objects.filter(editorial_types__type__slug="news")
            .live()
            .filter(show_on_home_page=True)
            .order_by("-published_at")[:NEWS_ITEMS]
        )
        news_and_events_content = list(chain(news, event))

        return [
            self.related_news_events_formatter(page, editorial_meta_label="News")
            for page in news_and_events_content
        ]

    def get_alumni_stories(self):
        if self.use_api_for_alumni_stories:
            return get_api_alumni_stories()
        pages_queryset = (
            EditorialPage.objects.filter(editorial_types__type__slug="alumni-story")
            .live()
            .order_by("-published_at")[:3]
        )
        return [
            self.related_news_events_formatter(
                page, editorial_meta_label="Alumni story", long_description=True
            )
            for page in pages_queryset
        ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["transformation_block"] = self.transformation_blocks.select_related(
            "image"
        ).first()
        context["partnerships_block"] = self._format_partnerships(
            self.partnerships_block.first()
        )

        context["stats_block"] = self.stats_block.select_related(
            "background_image"
        ).first()

        # TODO Work in if checks for pulling api content here
        context["news_and_events"] = self.get_news_and_events()
        context["alumni_stories"] = self.get_alumni_stories()
        context["hero_colour"] = LIGHT_HERO
        if self.tap_widget:
            context["tap_widget_code"] = mark_safe(self.tap_widget.script_code)

        if (
            hasattr(self, "hero_colour_option")
            and self.hero_colour_option == DARK_TEXT_ON_LIGHT_IMAGE
        ):
            context["hero_colour"] = DARK_HERO

        return context
