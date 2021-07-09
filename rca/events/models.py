import datetime

from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from rca.utils.models import BasePage


class EventIndexPage(BasePage):
    subpage_types = ["EventDetailPage"]
    template = "patterns/pages/events/event_index_page.html"

    # TODO: add fields to this placeholder model (needed as event detail parent)


class EventDetailPage(BasePage):
    parent_page_types = ["EventIndexPage"]
    subpage_types = []
    template = "patterns/pages/events/event_detail.html"

    hero_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    start_date = models.DateField(help_text="Enter the start date of the event.")
    end_date = models.DateField(
        help_text="Enter the end date of the event. This will be the same as "
        "the start date for single day events."
    )
    asset_heading = models.CharField(
        blank=True,
        max_length=40,
        verbose_name="Heading",
    )
    asset_link_text = models.CharField(
        blank=True,
        max_length=40,
        verbose_name="Link Text",
    )
    asset_link = models.URLField(
        blank=True,
        max_length=255,
        verbose_name="Link URL",
    )
    introduction = models.TextField()

    content_panels = BasePage.content_panels + [
        ImageChooserPanel("hero_image"),
        MultiFieldPanel(
            [
                FieldPanel("start_date"),
                FieldPanel("end_date"),
            ],
            heading="Event Dates",
        ),
        MultiFieldPanel(
            [
                FieldPanel("asset_heading"),
                FieldPanel("asset_link_text"),
                FieldPanel("asset_link"),
            ],
            heading="Asset Download",
        ),
        FieldPanel("introduction"),
    ]

    search_fields = BasePage.search_fields + [index.SearchField("introduction")]

    @property
    def event_date(self):
        if self.start_date == self.end_date:
            return f"{self.end_date:%d %B %Y}"
        return f"{self.start_date:%d %B} - {self.end_date:%d %B %Y}"

    @property
    def past(self):
        return self.end_date < datetime.date.today()

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update(hero_image=self.hero_image)
        return context
