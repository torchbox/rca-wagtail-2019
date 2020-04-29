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
from rca.utils.blocks import RelatedPageListBlock, StatisticBlock
from rca.utils.models import BasePage, LinkFields, RelatedPage


class FeaturedImage(LinkFields):
    title = models.TextField(max_length=80, blank=True)
    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    subtitle = models.TextField(max_length=120, blank=True)
    description = models.TextField(max_length=250, blank=True)

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
    title = models.CharField(max_length=125)
    statistics = StreamField([("statistic", StatisticBlock())])
    background_image = models.ForeignKey(
        get_image_model_string(),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    link_url = models.URLField(blank=True)
    link_text = models.CharField(blank=True, max_length=255)
    panels = [
        FieldPanel("title"),
        ImageChooserPanel("background_image"),
        StreamFieldPanel("statistics"),
        FieldPanel("link_url"),
        FieldPanel("link_text"),
    ]

    def __str__(self):
        return self.title


class LandingPageFeaturedImage(FeaturedImage):
    source_page = ParentalKey("LandingPage", related_name="featured_image")


class LandingPageFeaturedImageSecondary(FeaturedImage):
    # There are 2 features images in places, this may then work better as a streamfield...
    # TODO ?
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


"""
TODO Explain this class, and the other classes better
- why this isn't abstract
- how we relabel fields
- why did I do this?
"""


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
    introduction = models.TextField(max_length=500, blank=True)
    about_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    highlights_title = models.TextField(max_length=80, blank=True)
    highlights_link_url = models.URLField(
        blank=True, help_text=("Optional link to more information")
    )
    highlights_link_text = models.CharField(
        max_length=80, blank=True, help_text=_("The text to display for the link")
    )

    related_pages_title = models.TextField(
        max_length=80,
        blank=True,
        help_text=_("The title to be displayed above the related pages grid"),
    )
    related_pages_text = models.TextField(
        max_length=250,
        blank=True,
        help_text=_(
            "The brief paragraph of text to be displayed above the related pages grid"
        ),
    )
    page_list_title = models.TextField(
        max_length=80,
        blank=True,
        help_text=_("The title to be displayed above the page list blocks"),
    )
    page_list = StreamField([("page_list", RelatedPageListBlock())], blank=True)

    contact_title = models.CharField(max_length=120, blank=True)
    contact_text = models.CharField(max_length=250, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_url = models.URLField(blank=True, verbose_name="Contact URL")
    contact_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=False,
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
            heading=_("Course Introduction"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("highlights_title"),
                InlinePanel("related_pages_highlights", label=_("Page"), max_num=8),
                FieldPanel("highlights_link_url"),
                FieldPanel("highlights_link_text"),
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
        for page in pages:
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
        return items[:8]

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
            }
            for page in block.value["page"]:
                page = page.value.specific
                item["related_items"].append(page)
            items.append(item)
        return items

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["hero_colour"] = DARK_HERO
        if int(self.hero_colour_option) == LIGHT_TEXT_ON_DARK_IMAGE:
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
        return context


class ResearchLandingPage(LandingPage):
    template = "patterns/pages/landingpage/landing_page--research.html"
    content_panels = [
        InlinePanel("featured_image", label=_("Featured image"), max_num=1)
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
            heading=_("Course Introduction"),
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
                FieldPanel("highlights_link_url"),
                FieldPanel("highlights_link_text"),
            ],
            heading=_("Pages carousel"),
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


# Some field renaming, as we are re-using lot's of the fields, this will present the field in
# the CMS with a name that makes more sense
InnovationLandingPage._meta.get_field("highlights_title").verbose_name = _("Title")
InnovationLandingPage._meta.get_field("highlights_link_url").verbose_name = _("Link")
InnovationLandingPage._meta.get_field("highlights_link_text").verbose_name = _(
    "Link text"
)


class EnterpriseLandingPage(LandingPage):
    template = "patterns/pages/landingpage/landing_page--enterprise.html"

    class Meta:
        verbose_name = "Landing Page - Enterprise"
