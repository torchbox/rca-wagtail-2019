from django.db import models
from django.utils.text import slugify
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField

from rca.scholarships.blocks import ScholarshipsListingPageBlock
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet

from rca.programmes.models import ProgrammePage
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


@register_snippet
class Scholarship(models.Model):
    title = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    summary = models.CharField(max_length=255)
    eligable_programmes = models.ManyToManyField(ProgrammePage)
    funding_categories = models.ManyToManyField(ScholarshipFunding)
    fee_statuses = models.ManyToManyField(ScholarshipFeeStatus)


class ScholarshipsListingPage(ContactFieldsMixin, BasePage):
    template = "patterns/pages/scholarships/scholarships_listing_page.html"
    max_count = 1
    introduction = models.CharField(max_length=500, blank=True)
    body = StreamField(ScholarshipsListingPageBlock())
    lower_body = StreamField(ScholarshipsListingPageBlock())

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        StreamFieldPanel("body"),
        StreamFieldPanel("lower_body"),
        MultiFieldPanel([*ContactFieldsMixin.panels], heading="Contact information"),
    ]

    def anchor_nav(self):
        """Build list of data to be used as in-page navigation"""
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
