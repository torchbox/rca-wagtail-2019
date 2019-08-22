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
from wagtail.core.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel

from rca.utils.blocks import SlideBlock, StatisticBlock
from rca.utils.models import BasePage


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
    hero_colour_option = models.CharField(
        max_length=1,
        choices=(
            ("1", "Light text on a dark image"),
            ("2", "Dark text on a light image"),
        ),
    )
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

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["hero_colour"] = "dark"
        if self.hero_colour_option == "1":
            context["hero_colour"] = "light"

        context["transformation_blocks"] = self.transformation_blocks.select_related(
            "image"
        )
        context["partnerships_block"] = HomePagePartnershipBlock.objects.filter(
            source_page=self
        ).first
        context["stats_block"] = self.stats_block.select_related("background_image")

        return context
