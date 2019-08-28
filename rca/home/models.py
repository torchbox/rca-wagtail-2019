from collections import defaultdict
from datetime import datetime

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    StreamFieldPanel,
)
from wagtail.core.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel

from rca.utils.blocks import SlideBlock, StatisticBlock
from rca.utils.models import BasePage

LIGHT_TEXT_ON_DARK_IMAGE = 1
DARK_TEXT_ON_LIGHT_IMAGE = 2

HERO_COLOUR_CHOICES = (
    (LIGHT_TEXT_ON_DARK_IMAGE, "Light text on dark image"),
    (DARK_TEXT_ON_LIGHT_IMAGE, "dark text on light image"),
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
        help_text="The text dipsplayed next to the video play button",
    )
    sub_heading = models.CharField(
        max_length=125, blank=True, help_text="The title below the image"
    )
    page_title = models.CharField(
        max_length=125, blank=True, help_text="A title for the linked related page"
    )
    page_summary = models.CharField(
        max_length=250, blank=True, help_text="A summary for the linked related page"
    )
    page_link_url = models.URLField(blank=True, help_text="A url to a related page")

    panels = [
        FieldPanel("heading"),
        ImageChooserPanel("image"),
        FieldPanel("video"),
        FieldPanel("video_caption"),
        FieldPanel("sub_heading"),
        FieldPanel("page_title"),
        FieldPanel("page_summary"),
        FieldPanel("page_link_url"),
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
    slides = StreamField([("slide", SlideBlock())])
    panels = [FieldPanel("title"), FieldPanel("summary"), StreamFieldPanel("slides")]

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
        ImageChooserPanel("background_image"),
        StreamFieldPanel("statistics"),
    ]

    def __str__(self):
        return self.title


class HomePage(BasePage):
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
    hero_cta_text = models.CharField(max_length=125, blank=True)
    hero_cta_sub_text = models.CharField(max_length=125, blank=True)

    strapline = models.CharField(max_length=125)
    strapline_cta_url = models.URLField(blank=True)
    strapline_cta_text = models.CharField(max_length=125, blank=True)

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                ImageChooserPanel("hero_image"),
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
        InlinePanel("transformation_blocks", label="Transormation block", max_num=1),
        InlinePanel("partnerships_block", label="Partnerships", max_num=1),
        InlinePanel("stats_block", label="Statistics", max_num=1),
    ]

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

    def pull_event(self):
        # TODO extend the api to allow querying the latest event dates_times__date_from
        # This is waiting to be merged to RCA, for now use ID
        # eg /api/v2/pages/?limit=1&event_date_from=True&type=rca.EventItem

        url = "https://www.rca.ac.uk/api/v2/pages/?limit=1&order=-id&type=rca.EventItem"
        resp = requests.get(url=url)
        data = resp.json()
        _data = []
        for item in data["items"]:
            _item = {}
            # an extra qurey for more information is needed
            detail = item["meta"]["detail_url"] + "?fields=_,dates_times,feed_image"
            resp = requests.get(url=detail)
            data = resp.json()
            feed_image = data["feed_image"]["meta"]["detail_url"]
            feed_image = requests.get(url=feed_image)
            feed_image = feed_image.json()
            feed_image = feed_image["original"]["url"]
            date = data["dates_times"][0]["date_from"]
            date = datetime.strptime(date, "%Y-%m-%d")
            date = date.strftime("%-d %B %Y")
            _item["title"] = item["title"]
            _item["type"] = "Event"
            _item["description"] = date
            _item["image"] = feed_image
            _item["link"] = item["meta"]["html_url"]
            _data.append(_item)
        return _data

    def pull_news(self):
        url = (
            "https://www.rca.ac.uk/api/v2/pages/?limit=2&order=-date&type=rca.NewsItem"
        )
        resp = requests.get(url=url)
        data = resp.json()
        _data = []
        for item in data["items"]:
            _item = {}
            # an extra qurey for more information is needed
            detail = item["meta"]["detail_url"] + "?fields=_,date,feed_image"
            resp = requests.get(url=detail)
            data = resp.json()
            feed_image = data["feed_image"]["meta"]["detail_url"]
            feed_image = requests.get(url=feed_image)
            feed_image = feed_image.json()
            feed_image = feed_image["original"]["url"]
            date = data["date"]
            date = datetime.strptime(date, "%Y-%m-%d")
            date = date.strftime("%-d %B %Y")
            _item["title"] = item["title"]
            _item["type"] = "News"
            _item["description"] = date
            _item["image"] = feed_image
            _item["link"] = item["meta"]["html_url"]
            _data.append(_item)
        return _data

    def pull_alumni_stories(self):
        url = (
            "https://www.rca.ac.uk/api/v2/pages/?type=rca.StandardPage&tags=alumni-story&"
            "order=-first_published_at&limit=3"
        )
        resp = requests.get(url=url)
        data = resp.json()
        _data = []
        for item in data["items"]:
            _item = {}
            # an extra qurey for more information is needed
            detail = item["meta"]["detail_url"] + "?fields=_,feed_image,intro"
            resp = requests.get(url=detail)
            data = resp.json()
            if "feed_image" in data:
                feed_image = data["feed_image"]["meta"]["detail_url"]
                feed_image = requests.get(url=feed_image)
                feed_image = feed_image.json()
                feed_image = feed_image["original"]["url"]
                _item["image"] = feed_image
            _item["title"] = item["title"]
            _item["type"] = "Alumni Story"
            _item["description"] = data["intro"]

            _item["link"] = item["meta"]["html_url"]
            _data.append(_item)
        return _data

    def get_news(self):
        if not cache.get("latest_news"):
            cache.set("latest_news", self.pull_news(), settings.API_CONTENT_CACHE)
        return cache.get("latest_news")

    def get_event(self):
        if not cache.get("latest_event"):
            cache.set("latest_event", self.pull_event(), settings.API_CONTENT_CACHE)
        return cache.get("latest_event")

    def get_alumni_stories(self):
        if not cache.get("latest_alumni_stories"):
            cache.set(
                "latest_alumni_stories",
                self.pull_alumni_stories(),
                settings.API_CONTENT_CACHE,
            )
        return cache.get("latest_alumni_stories")

    def get_context(self, request, *args, **kwargs):
        # cache.clear()
        context = super().get_context(request, *args, **kwargs)
        context["hero_colour"] = "dark"

        if self.hero_colour_option == LIGHT_TEXT_ON_DARK_IMAGE:
            context["hero_colour"] = "light"

        context["transformation_block"] = self.transformation_blocks.select_related(
            "image"
        ).first()
        context["partnerships_block"] = self.partnerships_block.first()
        context["stats_block"] = self.stats_block.select_related(
            "background_image"
        ).first()
        context["news_and_events"] = self.get_news() + self.get_event()
        context["alumni_stories"] = self.get_alumni_stories()

        return context
