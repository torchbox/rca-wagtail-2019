from collections import defaultdict

from django.core.exceptions import ValidationError
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    StreamFieldPanel,
)
from wagtail.core.fields import StreamBlock, StreamField
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel

from rca.api_content.content import get_alumni_stories, get_news_and_events
from rca.utils.blocks import RelatedPageListBlockPage, StatisticBlock
from rca.utils.models import HERO_COLOUR_CHOICES, BasePage


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
    slides = StreamField(StreamBlock([("Page", RelatedPageListBlockPage())], max_num=1))

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

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                ImageChooserPanel("hero_image"),
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

    def _format_partnerships(self, partnerships_block):
        # The partnerships.slides field offers choice between a page
        # or a custom teaser, this method formats the data so either values
        # can be sent to the homepage template and format into a slideshow
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
                                "link": block.value["link"],
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

        context["news_and_events"] = get_news_and_events()
        context["alumni_stories"] = get_alumni_stories()

        return context
