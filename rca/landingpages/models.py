from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.core.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel

from rca.home.models import (
    DARK_HERO,
    HERO_COLOUR_CHOICES,
    LIGHT_HERO,
    LIGHT_TEXT_ON_DARK_IMAGE,
)
from rca.utils.blocks import (
    CallToActionBlock,
    RelatedPageListBlock,
    SlideBlock,
    StatisticBlock,
)
from rca.utils.models import BasePage, LinkFields, RelatedPage


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
        ImageChooserPanel("image"),
        FieldPanel("subtitle"),
        FieldPanel("description"),
    ] + LinkFields.panels

    class Meta:
        abstract = True


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
        ImageChooserPanel("background_image"),
        StreamFieldPanel("statistics"),
        PageChooserPanel("page_link"),
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
    panels = [PageChooserPanel("page")]


class LandingPageRelatedPageHighlights(RelatedPage):
    source_page = ParentalKey(
        "landingpages.LandingPage", related_name="related_pages_highlights"
    )
    panels = [PageChooserPanel("page")]


class HomePageSlideshowBlock(models.Model):
    source_page = ParentalKey("LandingPage", related_name="slideshow_block")
    title = models.CharField(
        max_length=125, help_text=_("Maximum length of 125 characters")
    )
    summary = models.CharField(
        max_length=250, blank=True, help_text=_("Maximum length of 250 characters")
    )
    slides = StreamField([("slide", SlideBlock())])
    panels = [FieldPanel("title"), FieldPanel("summary"), StreamFieldPanel("slides")]

    def __str__(self):
        return self.title


class LandingPage(BasePage):
    """ Defines all the fields we will need for the other versions of landing pages
    visibility of some extra fields that aren't needed on certain models which inherit LandingPage
    are controlled at the content_panels level"""

    template = "patterns/pages/landingpage/landing_page--generic.html"
    hero_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_colour_option = models.PositiveSmallIntegerField(choices=(HERO_COLOUR_CHOICES))
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
        max_length=80, blank=True, help_text=_("Maximum length of 80 characters")
    )
    highlights_page_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
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
    cta_block = StreamField([("call_to_action", CallToActionBlock())], blank=True)
    contact_title = models.CharField(
        max_length=120, blank=True, help_text=_("Maximum length of 120 characters")
    )
    contact_text = models.CharField(
        max_length=250, blank=True, help_text=_("Maximum length of 250 characters")
    )
    contact_email = models.EmailField(blank=True)
    contact_url = models.URLField(blank=True, verbose_name="Contact URL")
    contact_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [ImageChooserPanel("hero_image"), FieldPanel("hero_colour_option")],
            heading=_("Hero"),
        ),
        MultiFieldPanel(
            [FieldPanel("introduction"), PageChooserPanel("about_page")],
            heading=_("Introduction"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("highlights_title"),
                InlinePanel("related_pages_highlights", label=_("Page"), max_num=8),
            ],
            heading=_("Highlight pages carousel"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("related_pages_title"),
                FieldPanel("related_pages_text"),
                InlinePanel("related_pages_grid", max_num=8, label=_("Related Pages")),
            ],
            heading=_("Related pages grid"),
        ),
        InlinePanel("featured_image", label=_("Featured image"), max_num=1),
        MultiFieldPanel(
            [FieldPanel("page_list_title"), StreamFieldPanel("page_list")],
            heading=_("Related page list"),
        ),
    ]

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

    def get_featured_image(self):
        if hasattr(self, "featured_image"):
            return self.featured_image.first

    def get_featured_image_secondary(self):
        if hasattr(self, "featured_image_secondary"):
            return self.featured_image_secondary.first

    def get_related_pages(self, pages):
        related_pages = []
        for value in pages.select_related("page"):
            if value.page and value.page.live:
                page = value.page.specific
                related_pages.append(
                    {
                        "title": page.title,
                        "link": page.url,
                        "image": page.hero_image
                        if hasattr(page, "hero_image") and page.hero_image
                        else page.listing_image,
                        "description": page.introduction
                        if hasattr(page, "introduction")
                        else page.listing_summary,
                    }
                )
        return related_pages

    def get_page_list(self):
        """ Formats the related items coming from streamfield blocks
        into a digestable list for the template"""
        items = []
        for block in self.page_list:
            item = {
                "title": block.value["heading"],
                "related_items": [],
                "link": block.value["link"],
                "page_link": block.value["page_link"],
            }
            for page in block.value["page"]:
                page = page.value.specific
                item["related_items"].append(page)
            items.append(item)
        return items

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["hero_colour"] = DARK_HERO
        if self.hero_colour_option == LIGHT_TEXT_ON_DARK_IMAGE:
            context["hero_colour"] = LIGHT_HERO
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
        return context


class ResearchLandingPage(LandingPage):
    template = "patterns/pages/landingpage/landing_page--research.html"
    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [ImageChooserPanel("hero_image"), FieldPanel("hero_colour_option")],
            heading=_("Hero"),
        ),
        MultiFieldPanel(
            [FieldPanel("introduction"), PageChooserPanel("about_page")],
            heading=_("Introduction"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("highlights_title"),
                InlinePanel("related_pages_highlights", label=_("Page"), max_num=8),
                PageChooserPanel("highlights_page_link"),
            ],
            heading=_("Highlight pages carousel"),
        ),
        MultiFieldPanel(
            [FieldPanel("page_list_title"), StreamFieldPanel("page_list")],
            heading=_("Related page list"),
        ),
        InlinePanel("featured_image", label=_("Featured image"), max_num=1),
        InlinePanel("slideshow_block", label=_("Slideshow"), max_num=1),
        StreamFieldPanel("cta_block"),
        MultiFieldPanel(
            [
                ImageChooserPanel("contact_image"),
                FieldPanel("contact_title"),
                FieldPanel("contact_text"),
                FieldPanel("contact_email"),
                FieldPanel("contact_url"),
            ],
            heading="Contact information",
        ),
    ]

    class Meta:
        verbose_name = "Landing Page - Research"


class InnovationLandingPage(LandingPage):
    template = "patterns/pages/landingpage/landing_page--innovation.html"

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [ImageChooserPanel("hero_image"), FieldPanel("hero_colour_option")],
            heading=_("Hero"),
        ),
        MultiFieldPanel(
            [FieldPanel("introduction"), PageChooserPanel("about_page")],
            heading=_("Introduction"),
        ),
        MultiFieldPanel(
            [InlinePanel("featured_image", label=_("Featured image"), max_num=1)],
            heading=_("Highlight Image"),
        ),
        MultiFieldPanel(
            [FieldPanel("page_list_title"), StreamFieldPanel("page_list")],
            heading=_("Related page list"),
        ),
        InlinePanel("stats_block", label="Statistics", max_num=1),
        MultiFieldPanel(
            [
                FieldPanel("highlights_title"),
                InlinePanel("related_pages_highlights", label=_("Page"), max_num=8),
                PageChooserPanel("highlights_page_link"),
            ],
            heading=_("Featured projects"),
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    "featured_image_secondary", label=_("Featured image"), max_num=1
                )
            ],
            heading=_("Lower image feature"),
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel("contact_image"),
                FieldPanel("contact_title"),
                FieldPanel("contact_text"),
                FieldPanel("contact_email"),
                FieldPanel("contact_url"),
            ],
            heading="Contact information",
        ),
    ]

    class Meta:
        verbose_name = "Landing Page - Innovation"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["featured_image_secondary"] = self.get_featured_image_secondary()
        context["page_list"] = self.get_page_list()

        return context


class EnterpriseLandingPage(LandingPage):
    template = "patterns/pages/landingpage/landing_page--enterprise.html"

    class Meta:
        verbose_name = "Landing Page - Enterprise"
