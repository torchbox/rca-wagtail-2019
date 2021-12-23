from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel

from rca.utils.models import BasePage, ContactFieldsMixin


class ScholarshipsListingPage(ContactFieldsMixin, BasePage):
    template = "patterns/pages/scholarships/scholarships_listing_page.html"
    max_count = 1
    introduction = models.CharField(max_length=500, blank=True)
    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        MultiFieldPanel([*ContactFieldsMixin.panels], heading="Contact information"),
    ]
