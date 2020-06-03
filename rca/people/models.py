from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel

from rca.utils.blocks import AccordionBlockWithTitle, GalleryBlock, LinkBlock
from rca.utils.models import BasePage


class AreaOfExpertise(models.Model):
    title = models.CharField(max_length=128)

    def __str__(self):
        return self.title


class StaffPageAreOfExpertisePlacement(models.Model):
    page = ParentalKey("StaffPage", related_name="related_area_of_expertise")
    area_of_expertise = models.ForeignKey(
        AreaOfExpertise, on_delete=models.CASCADE, related_name="related_staff"
    )
    panels = [FieldPanel("area_of_expertise")]


class StaffPage(BasePage):
    template = "patterns/pages/staff/staff_detail.html"
    staff_title = models.CharField(
        max_length=255, help_text=_("E.G Dr, Professor"), blank=True
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    profile_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )

    job_title = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    introduction = models.TextField(blank=True)
    body = RichTextField(blank=True)

    research_highlights_title = models.CharField(
        max_length=120,
        blank=True,
        help_text=_(
            "The title value displayed above the Research highlights gallery showing project pages"
        ),
    )
    gallery = StreamField(
        [("slide", GalleryBlock())], blank=True, verbose_name=_("Gallery")
    )
    more_information_title = models.CharField(max_length=80, default="More information")
    more_information = StreamField(
        [("accordion_block", AccordionBlockWithTitle())],
        blank=True,
        verbose_name=_("More information"),
    )
    related_links = StreamField(
        [("link", LinkBlock())], blank=True, verbose_name="Related Links"
    )

    key_details_panels = [
        InlinePanel(
            "related_research_centre_pages", label=_("Related Research Centres ")
        ),
        InlinePanel("related_schools_pages", label=_("Related Schools")),
        InlinePanel("related_area_of_expertise", label=_("Areas of Expertise")),
    ]

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("staff_title"),
                FieldPanel("first_name"),
                FieldPanel("last_name"),
                ImageChooserPanel("profile_image"),
            ],
            heading="Details",
        ),
        MultiFieldPanel([FieldPanel("email")], heading=_("Contact information")),
        FieldPanel("job_title"),
        FieldPanel("introduction"),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("research_highlights_title"),
                InlinePanel(
                    "related_project_pages", label=_("Project pages"), max_num=8
                ),
            ],
            heading=_("Research highlights gallery"),
        ),
        StreamFieldPanel("gallery"),
        MultiFieldPanel(
            [
                FieldPanel("more_information_title"),
                StreamFieldPanel("more_information"),
            ],
            heading=_("More information"),
        ),
        StreamFieldPanel("related_links"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )

    def format_research_highlights(self):
        """Internal method for formatting related projects to the correct
        structure for the gallery template

        Returns:
            List
        """
        items = []
        for page in self.related_projects.all():
            page = page.page.specific
            meta = None
            related_school = page.related_school_pages.first()
            if related_school is not None:
                meta = related_school.page.title

            items.append(
                {
                    "title": page.title,
                    "link": page.url,
                    "image": page.hero_image,
                    "description": page.introduction,
                    "meta": meta,
                }
            )
        return items

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["research_highlights"] = self.format_research_highlights()
        context["areas"] = self.related_area_of_expertise.all()
        context["related_schools"] = self.related_school_pages.all()
        context["research_centres"] = self.related_research_centre_pages.all()

        return context
