from django.core.exceptions import ValidationError
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

from rca.utils.blocks import (
    CallToActionBlock,
    RelatedPageListBlock,
    SlideBlock,
    StatisticBlock,
)
from rca.utils.models import (
    HERO_COLOUR_CHOICES,
    BasePage,
    LegacyNewsAndEventsMixin,
    LinkFields,
    RelatedPage,
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
        ImageChooserPanel("image"),
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
    panels = [FieldPanel("title"), FieldPanel("summary"), StreamFieldPanel("slides")]

    def __str__(self):
        return self.title


class LandingPage(LegacyNewsAndEventsMixin, BasePage):
    """ Defines all the fields we will need for the other versions of landing pages
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
    slideshow_title = models.CharField(
        max_length=125, help_text=_("Maximum length of 125 characters"), blank=True
    )
    slideshow_summary = models.CharField(
        max_length=250, blank=True, help_text=_("Maximum length of 250 characters")
    )
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
            heading=_("Featured projects"),
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
        FieldPanel('legacy_news_and_event_tags'),
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
                        "meta": meta,
                    }
                )
        return related_pages

    def get_page_list(self):
        """ Formats the related items coming from streamfield blocks
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
            page = slide.page.specific
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
            }
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
            heading=_("Featured projects"),
        ),
        FieldPanel('legacy_news_and_event_tags'),
        MultiFieldPanel(
            [FieldPanel("page_list_title"), StreamFieldPanel("page_list")],
            heading=_("Related page list"),
        ),
        InlinePanel("featured_image", label=_("Featured image"), max_num=1),
        MultiFieldPanel(
            [
                FieldPanel("slideshow_title"),
                FieldPanel("slideshow_summary"),
                InlinePanel("slideshow_page", label=_("Page")),
            ],
            heading=_("Slideshow"),
        ),
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

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # reset the slideshow block so it can be re-populated as it's set in
        # the parent context for other slideshow formats.
        context["slideshow_block"] = []
        if self.slideshow_page.first():
            context["slideshow_block"] = self._format_slideshow_pages(
                self.slideshow_page.all()
            )
        return context


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
        FieldPanel('legacy_news_and_event_tags'),
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
