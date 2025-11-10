import re

from django.db import models
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.search import index

from rca.utils.blocks import GuideBlock
from rca.utils.blocks.content import AccordionBlock
from rca.utils.fields import StreamField
from rca.utils.models import (
    BasePage,
    ContactFieldsMixin,
    RelatedPage,
    RelatedStaffPageWithManualOptions,
    StickyCTAMixin,
    TapMixin,
)
from rca.utils.shorthand import ShorthandContentMixin


class GuidePageStaff(RelatedStaffPageWithManualOptions):
    source_page = ParentalKey("guides.GuidePage", related_name="related_staff")


class GuidePageRelatedPages(RelatedPage):
    source_page = ParentalKey("guides.GuidePage", related_name="related_pages")


class GuidePage(
    ShorthandContentMixin, TapMixin, ContactFieldsMixin, StickyCTAMixin, BasePage
):
    template = "patterns/pages/guide/guide.html"

    introduction = models.CharField(max_length=500, blank=True)
    body = StreamField(GuideBlock(), blank=True)
    further_information_block = StreamField(
        [("accordion", AccordionBlock())],
        blank=True,
    )
    related_staff_title = models.CharField(blank=True, max_length=120, default="Staff")
    related_pages_title = models.CharField(blank=True, max_length=120)

    search_fields = ShorthandContentMixin.search_fields + [
        index.SearchField("introduction"),
        index.AutocompleteField("introduction"),
        index.SearchField("body"),
        index.SearchField("further_information_block"),
    ]

    content_panels = (
        BasePage.content_panels
        + [
            FieldPanel("introduction"),
            FieldPanel("shorthand_story_url"),
            FieldPanel("body"),
            MultiFieldPanel(
                [FieldPanel("related_staff_title"), InlinePanel("related_staff")],
                heading=_("Related staff"),
            ),
            MultiFieldPanel(
                [
                    FieldPanel("further_information_block"),
                ],
                heading=_("Further information"),
            ),
            MultiFieldPanel(
                [
                    FieldPanel("related_pages_title"),
                    InlinePanel("related_pages", max_num=6),
                ],
                heading=_("Related pages"),
            ),
            MultiFieldPanel(
                [*ContactFieldsMixin.panels], heading="Contact information"
            ),
        ]
        + TapMixin.panels
        + [StickyCTAMixin.panels]
    )

    @property
    def listing_meta(self):
        # Returns a page 'type' value that's readable for listings,
        return "Guide"

    def anchor_nav(self):
        """Build list of data to be used as
        in-page navigation"""
        items = []
        for i, block in enumerate(self.body):
            if block.block_type == "anchor_heading":
                items.append({"title": block.value, "link": f"#{slugify(block.value)}"})
        if self.related_staff.first():
            items.append({"title": self.related_staff_title, "link": "#staff"})
        if self.further_information_block:
            for block in self.further_information_block:
                items.append(
                    {
                        "title": block.value.get("heading"),
                        "link": f"#{slugify(block.value.get('heading'))}",
                    }
                )
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
            introduction = page.listing_summary
            if hasattr(page, "programme_description_subtitle"):
                introduction = page.programme_description_subtitle
            if hasattr(page, "introduction"):
                introduction = re.sub("<a.*?>|</a>", "", page.introduction)
            related_pages["items"].append(
                {
                    "page": page,
                    "title": page.listing_title if page.listing_title else page.title,
                    "image": page.listing_image,
                    "link": page.url,
                    "description": page.listing_summary or introduction,
                }
            )
        return related_pages

    def has_sticky_cta(self):
        data = self.get_sticky_cta()
        return all(data.get(key) for key in ["message", "action", "link"])

    def has_vepple_panorama(self):
        for value in self.body.raw_data:
            if value["type"] == "vepple_panorama":
                return True
        return False

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        if not self.shorthand_embed_code:
            context["anchor_nav"] = self.anchor_nav()
            context["related_staff"] = self.related_staff.all
            context["related_pages"] = self.get_related_pages()
        if self.has_sticky_cta():
            context["sticky_cta"] = self.get_sticky_cta()
        if self.tap_widget:
            context["tap_widget_code"] = mark_safe(self.tap_widget.script_code)

        return context
