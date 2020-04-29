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
    related_pages_title = models.CharField(blank=True, max_length=120)
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
        MultiFieldPanel(
            [
                FieldPanel("related_pages_title"),
                InlinePanel("related_pages", max_num=6),
            ],
            heading=_("Related pages"),
        ),
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
                items.append({"title": block.value, "link": f"#{slugify(block.value)}"})
        if self.related_staff.first():
            items.append({"title": "Staff", "link": "#staff"})
        if self.related_pages_title:
            items.append(
                {
                    "title": self.related_pages_title,
                    "link": f"#{slugify(self.related_pages_title)}",
                }
            )

        return items

    def get_related_pages(self):
        related_pages = {"title": self.related_pages_title, "items": []}
        for related_page in self.related_pages.all():
            page = related_page.page.specific
            related_pages["items"].append(
                {
                    "page": page,
                    "title": page.listing_title if page.listing_title else page.title,
                    "image": page.listing_image,
                    "link": page.url,
                    "description": page.listing_summary,
                }
            )
        return related_pages

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["anchor_nav"] = self.anchor_nav()
        context["related_staff"] = self.related_staff.all
        context["related_pages"] = self.get_related_pages()

        return context
