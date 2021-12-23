from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel

from rca.utils.models import BasePage, ContactFieldsMixin, SluggedTaxonomy


class ScholarshipFeeStatus(SluggedTaxonomy):
    panels = [
        FieldPanel('title'),
    ]

    class Meta:
        verbose_name_plural = "Scholarship Fee Statuses"


class ScholarshipFunding(SluggedTaxonomy):
    panels = [
        FieldPanel('title'),
    ]


class ScholarshipLocation(SluggedTaxonomy):
    panels = [
        FieldPanel('title'),
    ]


class ScholarshipsListingPage(ContactFieldsMixin, BasePage):
    template = "patterns/pages/scholarships/scholarships_listing_page.html"
    max_count = 1
    introduction = models.CharField(max_length=500, blank=True)
    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        MultiFieldPanel([*ContactFieldsMixin.panels], heading="Contact information"),
    ]
