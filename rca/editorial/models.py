from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
)
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


class EditorialPageAuthor(models.Model):
    page = ParentalKey("EditorialPage", related_name="editorial_authors")
    author = models.ForeignKey("Author", related_name="+", on_delete=models.CASCADE)
    panels = [FieldPanel("author")]

    def __str__(self):
        return self.author.name


class EditorialPageArea(models.Model):
    page = ParentalKey("EditorialPage", related_name="editorial_area")
    area = models.ForeignKey(
        "people.AreaOfExpertise", related_name="+", on_delete=models.CASCADE
    )
    panels = [FieldPanel("area")]

    def __str__(self):
        return self.area.title


class EditorialPage(BasePage):
    template = "patterns/pages/editorial/editorial_detail.html"
    intro_text = models.CharField(blank=True, max_length=255)
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
    video_preview_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    date = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(blank=True, max_length=254)
    # have not included date here as I tink it should be added automiatically
    content_panels = BasePage.content_panels + [
        FieldPanel("intro_text"),
        ImageChooserPanel("hero_image"),
        MultiFieldPanel(
            [
                FieldPanel("video"),
                FieldPanel("video_caption"),
                ImageChooserPanel("video_preview_image"),
            ],
            heading="Introductory Video",
        ),
    ]

    key_details_panels = [
        MultiFieldPanel(
            [
                InlinePanel(
                    "related_schools_and_research_pages",
                    label="School or Research Centre",
                ),
                InlinePanel("editorial_area", label="Area"),
            ],
            heading="Related School, Research Centre or Area",
        ),
        InlinePanel("editorial_authors", label="Editorial Authors"),
        FieldPanel("email"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )
