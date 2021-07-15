import datetime

from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from rca.utils.models import BasePage

from .blocks import CallToAction, EventDetailPageBlock, PartnersBlock


class EventIndexPage(BasePage):
    subpage_types = ["EventDetailPage"]
    template = "patterns/pages/events/event_index_page.html"

    # TODO: add fields to this placeholder model (needed as event detail parent)


class EventSeries(models.Model):
    title = models.CharField(max_length=128)
    introduction = models.TextField()

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


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
    series = models.ForeignKey(
        EventSeries,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="events",
    )
    introduction = RichTextField()
    body = StreamField(EventDetailPageBlock())
    partners_heading = models.CharField(
        blank=True, max_length=120, verbose_name="Heading"
    )
    partners = StreamField(PartnersBlock(), blank=True)
    call_to_action = StreamField(CallToAction(max_num=1, required=False), blank=True)

    content_panels = BasePage.content_panels + [
        ImageChooserPanel("hero_image"),
        MultiFieldPanel(
            [FieldPanel("start_date"), FieldPanel("end_date")], heading="Event Dates",
        ),
        FieldPanel("series"),
        FieldPanel("introduction"),
        StreamFieldPanel("body"),
        MultiFieldPanel(
            [FieldPanel("partners_heading"), StreamFieldPanel("partners")],
            heading="Partners",
        ),
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

    def get_series_events(self):
        today = datetime.date.today()
        return [
            {
                "title": e.title,
                "link": e.url,
                "meta": "",  # TODO: on separate ticket
                "description": e.introduction,
                "image": e.listing_image if e.listing_image else e.hero_image,
            }
            for e in (
                EventDetailPage.objects.filter(series=self.series, end_date__gt=today)
                .not_page(self)
                .live()
                .order_by("-end_date")
                .select_related("hero_image", "listing_image")
            )
        ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update(
            hero_image=self.hero_image,
            series_events=self.get_series_events() if self.series else [],
        )
        return context
