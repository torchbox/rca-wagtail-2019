from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.images.edit_handlers import ImageChooserPanel

from rca.home.models import (
    DARK_HERO,
    HERO_COLOUR_CHOICES,
    LIGHT_HERO,
    LIGHT_TEXT_ON_DARK_IMAGE,
)
from rca.utils.models import BasePage, LinkFields, RelatedPage


class FeaturedImage(LinkFields):
    title = models.TextField(max_length=80, blank=True)
    image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    subtitle = models.TextField(max_length=120, blank=True)
    description = models.TextField(max_length=250, blank=True)

    class Meta:
        abstract = True

    panels = [
        FieldPanel("title"),
        ImageChooserPanel("image"),
        FieldPanel("subtitle"),
        FieldPanel("description"),
    ] + LinkFields.panels


class LandingPageHighlightLinkField(LinkFields):
    source_page = ParentalKey("LandingPage", related_name="highlight_link")


class LandingPageAboutLinkField(LinkFields):
    source_page = ParentalKey("LandingPage", related_name="about_page")


class LandingPage(BasePage):
    """ Defines all the fields we will need for the other versions of landing pages"""

    # TODO Make this createable and act as the default
    is_creatable = False
    hero_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_colour_option = models.PositiveSmallIntegerField(choices=(HERO_COLOUR_CHOICES))
    introduction = models.TextField(max_length=500, blank=True)
    highlights_title = models.TextField(max_length=80, blank=True)

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [ImageChooserPanel("hero_image"), FieldPanel("hero_colour_option")],
            heading=_("Hero"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("introduction"),
                InlinePanel("about_page", label=_("About page")),
            ],
            heading=_("Course Introduction"),
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

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["hero_colour"] = DARK_HERO
        if int(self.hero_colour_option) == LIGHT_TEXT_ON_DARK_IMAGE:
            context["hero_colour"] = LIGHT_HERO
        context["about_page"] = self.about_page.first
        context["featured_image"] = self.get_featured_image()

        return context


class LandingPageDefaultFeaturedImage(FeaturedImage):
    # TODO change to foreign key
    source_page = ParentalKey(
        "landingpages.LandingPageDefault", related_name="featured_image"
    )


class LandingPageDefaultHighlightPages(RelatedPage):
    source_page = ParentalKey(
        "landingpages.LandingPageDefault", related_name="highlight_pages_default"
    )
    panels = [PageChooserPanel("page", ["projects.ProjectPage"])]


class LandingPageDefaultRelatedPages(RelatedPage):
    # TODO source page should be to LandingPage
    source_page = ParentalKey(
        "landingpages.LandingPageDefault", related_name="related_pages"
    )
    panels = [PageChooserPanel("page")]


class LandingPageDefaultRelatedProgrammesLinkField(LinkFields):
    source_page = ParentalKey(
        "LandingPageDefault", related_name="related_programmes_link"
    )


class LandingPageRelatedProgrammPages(RelatedPage):
    source_page = ParentalKey(
        "landingpages.LandingPage", related_name="related_programmes"
    )
    panels = [
        PageChooserPanel(
            "page", ["programmes.ProgrammePage", "shortcourses.ShortCoursePage"]
        )
    ]


class LandingPageDefault(LandingPage):
    template = "patterns/pages/landingpage/landing_page.html"

    class Meta:
        verbose_name = "Landing Page - Default"

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
    related_programmes_title = models.TextField(
        max_length=80,
        blank=True,
        help_text=_("The title to be displayed above the related pages"),
    )
    related_programmes_subtitle = models.TextField(
        max_length=80,
        blank=True,
        help_text=_("The subtitle, displayed above the related pages"),
    )

    content_panels = LandingPage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("highlights_title"),
                InlinePanel(
                    "highlight_pages_default", max_num=8, label=_("Highlight pages")
                ),
                InlinePanel("highlight_link", max_num=1, label=_("Read more link")),
            ],
            heading=_("Highlight pages carousel"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("related_pages_title"),
                FieldPanel("related_pages_text"),
                InlinePanel("related_pages", label=_("Related pages"), max_num=8),
            ],
            heading=_("Related pages"),
        ),
        InlinePanel("featured_image", label=_("Featured image"), max_num=1),
        MultiFieldPanel(
            [
                FieldPanel("related_programmes_title"),
                FieldPanel("related_programmes_subtitle"),
                InlinePanel(
                    "related_programmes", label=_("Related programmes"), max_num=8
                ),
                InlinePanel(
                    "related_programmes_link", label=_("View more link"), max_num=1
                ),
            ],
            heading=_("Related programmes"),
        ),
    ]

    def get_related_pages(self):
        related_pages = []
        for value in self.related_pages.select_related("page"):
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
                        else None,
                    }
                )
        return related_pages

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["highlight_pages"] = self._format_projects_for_gallery(
            self.highlight_pages_default.all()
        )
        context["related_pages"] = self.get_related_pages()
        context["related_programmes"] = [
            {
                "title": self.related_programmes_title,
                "subtitle": self.related_programmes_subtitle,
                "related_items": [
                    rel.page.specific
                    for rel in self.related_programmes.select_related("page")
                ],
            }
        ]

        return context


class ResearchLandingPage(LandingPage):
    template = "patterns/pages/landingpage/landing_page--research.html"

    class Meta:
        verbose_name = "Landing Page - Research"


class InnovationLandingPage(LandingPage):
    template = "patterns/pages/landingpage/landing_page--innovation.html"

    class Meta:
        verbose_name = "Landing Page - Innovation"


class EnterpriseLandingPage(LandingPage):
    template = "patterns/pages/landingpage/landing_page--enterprise.html"

    class Meta:
        verbose_name = "Landing Page - Enterprise"
