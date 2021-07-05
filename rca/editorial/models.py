from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.api import APIField
from wagtail.core.fields import RichTextField
from wagtail.images.edit_handlers import ImageChooserPanel

from rca.utils.models import BasePage, RelatedPage


class EditorialPageRelatedSchoolsAndResearchPages(RelatedPage):
    source_page = ParentalKey(
        "EditorialPage", related_name="related_schools_and_research_pages"
    )
    panels = [
        PageChooserPanel("page", ["schools.SchoolPage", "research.ResearchCentrePage"])
    ]

    api_fields = [APIField("page")]


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


class EditorialPage(BasePage):

    intro_text = RichTextField(blank=True, max_length=255)
    #  this is not on the base page
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

    #  do you want it to be from date created - auto_now_add (I think )
    #  or from date_updated = add_add
    date = models.DateTimeField(auto_now_add=True)

    # author - taxonomy - something to do with get_contenct on project page
    # create author taxonomy
    # foreign key to that taxoomy
    #  look at how newstype is done inn wagtail kit
    #  essnetially be doing the same thing for all texonomies
    #  dont do the frontned stuff

    #  create author app
    #  create author model
    #  do foreign key to that
    #

    # school_or_center = foreign key

    email = models.EmailField(blank=True, max_length=254)

    # def get_context(self, request, *args, **kwargs):
    #     context = super().get_context(request, *args, **kwargs)
    #     taxonomy_tags = []
    #     if self.related_school_pages:
    #         for i in self.related_school_pages.all():
    #             taxonomy_tags.append({"title": i.page.title})
    #     context["taxonomy_tags"] = taxonomy_tags

    #     return context

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
        FieldPanel("email"),
        MultiFieldPanel(
            [InlinePanel("related_schools_and_research_pages")],
            heading="Related Schools and Research Centres",
        ),
        InlinePanel("editorial_authors", label="Editorial Authors"),
    ]
