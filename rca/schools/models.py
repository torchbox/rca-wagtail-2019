from django.db import models
from django.http import Http404
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import FieldPanel, PageChooserPanel
from wagtail.api import APIField
from wagtail.core.models import Orderable, Page
from wagtail.search import index

from rca.utils.models import BasePage


class RelatedSchoolPage(Orderable):
    source_page = ParentalKey(Page, related_name="related_schools")
    page = models.ForeignKey("schools.SchoolPage", on_delete=models.CASCADE)

    panels = [PageChooserPanel("page")]


class SchoolPage(BasePage):
    template = "patterns/pages/schools/school_page.html"
    description = models.TextField(blank=True)
    content_panels = BasePage.content_panels + [FieldPanel("description")]
    search_fields = BasePage.search_fields + [index.SearchField("description")]

    api_fields = [APIField("description")]

    # Temporary, delete this method once SchoolPage development is complete.
    def serve(self, request):
        raise Http404
