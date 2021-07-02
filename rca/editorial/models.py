from django.db import models
from wagtail.core.fields import RichTextField

from rca.utils.models import BasePage

# from wagtail.admin.edit_handlers import PageChooserPanel
# from wagtail.core.fields import RichTextField, StreamField


# class EditorialPageRelatedSchoolsAndResearchPages(RelatedPage):
#     source_page = ParentalKey(
#         "ProgrammePage", related_name="related_schools_and_research_pages"
#     )
#     panels = [
#         PageChooserPanel("page", ["schools.SchoolPage", "research.ResearchCentrePage"])
#     ]

#     api_fields = [APIField("page")]


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

    # school_or_center = foreign key
    # project or programme model

    email = models.EmailField(blank=True, max_length=254)

    # def get_context(self, request, *args, **kwargs):
    #     context = super().get_context(request, *args, **kwargs)
    #     taxonomy_tags = []
    #     if self.related_school_pages:
    #         for i in self.related_school_pages.all():
    #             taxonomy_tags.append({"title": i.page.title})
    #     context["taxonomy_tags"] = taxonomy_tags

    #     return context
