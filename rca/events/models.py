import datetime

from django.db import models
from django.db.models.fields import SlugField
from django.utils.text import slugify
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from rca.utils.models import BasePage

from .blocks import CallToAction, EventDetailPageBlock


class EventType(models.Model):
    title = models.CharField(max_length=100)
    slug = SlugField()

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(EventType, self).save(*args, **kwargs)

    panels = [FieldPanel("title")]


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
    event_type = models.ForeignKey(
        EventType, null=True, on_delete=models.SET_NULL, related_name="events",
    )
    introduction = models.TextField()
    body = StreamField(EventDetailPageBlock())
    call_to_action = StreamField(CallToAction(max_num=1, required=False), blank=True)

    content_panels = BasePage.content_panels + [
        ImageChooserPanel("hero_image"),
        MultiFieldPanel(
            [FieldPanel("start_date"), FieldPanel("end_date")], heading="Event Dates",
        ),
        FieldPanel("event_type"),
        FieldPanel("introduction"),
        StreamFieldPanel("body"),
        StreamFieldPanel("call_to_action"),
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("body"),
    ]

    @property
    def event_date(self):
        if self.start_date == self.end_date:
            return f"{self.end_date:%d %B %Y}"
        return f"{self.start_date:%d %B} - {self.end_date:%d %B %Y}"

    @property
    def past(self):
        return self.end_date < datetime.date.today()

    @property
    def inline_cta(self):
        return self.call_to_action

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update(hero_image=self.hero_image)
        return context
