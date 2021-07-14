from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel

from rca.utils.models import BasePage, RelatedPage


class EditorialPageRelatedSchoolsAndResearchPages(RelatedPage):
    source_page = ParentalKey(
        "EditorialPage", related_name="related_schools_and_research_pages"
    )
    panels = [
        PageChooserPanel("page", ["schools.SchoolPage", "research.ResearchCentrePage"])
    ]


class Author(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class EditorialPageArea(models.Model):
    page = ParentalKey("EditorialPage", related_name="areas")
    area = models.ForeignKey(
        "people.AreaOfExpertise", related_name="editorial", on_delete=models.CASCADE
    )
    panels = [FieldPanel("area")]

    def __str__(self):
        return self.area.title


class EditorialPage(BasePage):
    template = "patterns/pages/editorial/editorial_detail.html"
    introduction = models.CharField(blank=True, max_length=255)
    hero_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    video = models.URLField(blank=True)
    video_caption = models.CharField(
        blank=True,
        max_length=80,
        help_text="The text displayed next to the video play button",
    )
    introduction_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    author = models.ForeignKey(
        "editorial.Author",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    published_at = models.DateField()
    contact_email = models.EmailField(blank=True, max_length=254)

    body = StreamField(
        [
            ("heading", blocks.CharBlock()),
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
            ("embed", EmbedBlock()),
        ],
        blank=True,
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        ImageChooserPanel("hero_image"),
        MultiFieldPanel(
            [
                FieldPanel("video"),
                FieldPanel("video_caption"),
                ImageChooserPanel("introduction_image"),
            ],
            heading="Introductory Video",
        ),
        StreamFieldPanel("body"),
    ]

    key_details_panels = [
        FieldPanel("published_at"),
        MultiFieldPanel(
            [
                InlinePanel(
                    "related_schools_and_research_pages",
                    label="School or Research Centre",
                ),
                InlinePanel("areas", label="Area"),
            ],
            heading="Related School, Research Centre or Area",
        ),
        FieldPanel("author"),
        FieldPanel("contact_email"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        taxonomy_tags = []

        if self.related_schools_and_research_pages:
            for related_page in self.related_schools_and_research_pages.all():
                taxonomy_tags.append({"title": related_page.page.title})
        if self.areas:
            for area in self.areas.all():
                taxonomy_tags.append({"title": area})

        context["taxonomy_tags"] = taxonomy_tags
        context["hero_image"] = self.hero_image

        return context
