from django.db import models
from django.http import Http404
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.api import APIField
from wagtail.search import index

from rca.utils.models import BasePage


class SchoolPage(BasePage):
    template = "patterns/pages/schools/school_page.html"
    description = models.TextField(blank=True)
    content_panels = BasePage.content_panels + [FieldPanel("description")]
    search_fields = BasePage.search_fields + [index.SearchField("description")]

    api_fields = [APIField("description")]

    # Temporary, delete this method once SchoolPage development is complete.
    def serve(self, request):
        raise Http404
