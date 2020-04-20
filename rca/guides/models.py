from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    StreamFieldPanel,
)
from wagtail.core.fields import StreamField
from wagtail.images.edit_handlers import ImageChooserPanel

from rca.utils.blocks import AccordionBlockWithTitle, GuideBlock
from rca.utils.models import BasePage, RelatedPage, RelatedStaffPageWithManualOptions


class GuidePageStaff(RelatedStaffPageWithManualOptions):
    source_page = ParentalKey("guides.GuidePage", related_name="related_staff")


class GuidePageRelatedPages(RelatedPage):
    source_page = ParentalKey("guides.GuidePage", related_name="related_pages")


class GuidePage(BasePage):
    template = "patterns/pages/guide/guide.html"

    introduction = models.CharField(max_length=500, blank=True)
    body = StreamField(GuideBlock())
    further_information = StreamField(
        [("accordion_block", AccordionBlockWithTitle())],
        blank=True,
        verbose_name=_("Further information"),
    )
    contact_email = models.EmailField(blank=True)
    contact_url = models.URLField(blank=True)
    contact_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    contact_text = models.TextField(blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        StreamFieldPanel("body"),
        MultiFieldPanel([InlinePanel("related_staff")], heading=_("Related staff")),
        StreamFieldPanel("further_information"),
        MultiFieldPanel([InlinePanel("related_pages")], heading=_("Related pages")),
        MultiFieldPanel(
            [
                ImageChooserPanel("contact_image"),
                FieldPanel("contact_text"),
                FieldPanel("contact_url"),
                FieldPanel("contact_email"),
            ],
            heading="Contact information",
        ),
    ]

    def anchor_nav(self):
        """ Build list of data to be used as
        in-page navigation """
        items = []
        for i, block in enumerate(self.body):
            if block.block_type == "anchor_heading":
                print(block.__dict__)
                items.append({"title": block.value, "link": f"#{slugify(block.value)}"})
        if self.related_staff:
            items.append({"title": "Staff", "link": "#staff"})

        return items

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["anchor_nav"] = self.anchor_nav()
        context["related_staff"] = self.related_staff.all
        context["related_pages"] = self.related_pages.all

        return context
