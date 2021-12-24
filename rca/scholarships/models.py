from django.db import models
from django.utils.text import slugify
from wagtail.admin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    ObjectList,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.core.fields import RichTextField, StreamField

from rca.scholarships.blocks import ScholarshipsListingPageBlock
from rca.utils.blocks import CallToActionBlock
from rca.utils.models import BasePage, ContactFieldsMixin, SluggedTaxonomy


class ScholarshipFeeStatus(SluggedTaxonomy):
    panels = [
        FieldPanel("title"),
    ]

    class Meta:
        verbose_name_plural = "Scholarship Fee Statuses"


class ScholarshipFunding(SluggedTaxonomy):
    panels = [
        FieldPanel("title"),
    ]


class ScholarshipLocation(SluggedTaxonomy):
    panels = [
        FieldPanel("title"),
    ]


class ScholarshipsListingPage(ContactFieldsMixin, BasePage):
    template = "patterns/pages/scholarships/scholarships_listing_page.html"
    max_count = 1
    introduction = models.CharField(max_length=500, blank=True)
    body = StreamField(ScholarshipsListingPageBlock())
    characteristics_disclaimer = models.CharField(
        max_length=250,
        blank=True,
        help_text="A small disclaimer shown just above the scholarships listing.",
    )
    lower_body = StreamField(ScholarshipsListingPageBlock())

    key_details = RichTextField(features=["h3", "bold", "italic", "link"], blank=True)
    form_introduction = models.CharField(max_length=500, blank=True)
    cta_block = StreamField(
        [("call_to_action", CallToActionBlock(label="text promo"))],
        blank=True,
        verbose_name="Call to action",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        StreamFieldPanel("body"),
        MultiFieldPanel(
            [FieldPanel("characteristics_disclaimer")], heading="Scholarship listing"
        ),
        StreamFieldPanel("lower_body"),
        MultiFieldPanel([*ContactFieldsMixin.panels], heading="Contact information"),
    ]

    form_settings_pannels = [
        FieldPanel("key_details"),
        FieldPanel("form_introduction"),
        StreamFieldPanel("cta_block"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
            ObjectList(form_settings_pannels, heading="Enquiry form settings"),
        ]
    )

    def anchor_nav(self):
        """ Build list of data to be used as in-page navigation """
        items = []
        blocks = []

        for block in self.body:
            blocks.append(block)
        for block in self.lower_body:
            blocks.append(block)

        for i, block in enumerate(blocks):
            if block.block_type == "anchor_heading":
                items.append({"title": block.value, "link": f"#{slugify(block.value)}"})
        return items

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["anchor_nav"] = self.anchor_nav()
        return context
