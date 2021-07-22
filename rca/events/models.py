import datetime

from django.db import models
from django.db.models.fields import SlugField
from django.utils.text import slugify
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from rca.utils.models import BasePage

from .blocks import CallToAction, EventDetailPageBlock, PartnersBlock


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


class EventEligibility(models.Model):
    title = models.CharField(max_length=100)
    slug = SlugField()

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    panels = [FieldPanel("title")]


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
    event_type = models.ForeignKey(
        EventType, null=True, on_delete=models.SET_NULL, related_name="events",
    )
    eligibility = models.ForeignKey(
        EventEligibility,
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
    partners = StreamField(PartnersBlock(required=False), blank=True)
    call_to_action = StreamField(CallToAction(required=False), blank=True)

    content_panels = BasePage.content_panels + [
        ImageChooserPanel("hero_image"),
        MultiFieldPanel(
            [FieldPanel("start_date"), FieldPanel("end_date")], heading="Event Dates",
        ),
        MultiFieldPanel(
            [FieldPanel("event_type"), FieldPanel("series"), FieldPanel("eligibility")],
            heading="Event Taxonomy",
        ),
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
            return f"{self.end_date:%-d %B %Y}"
        return f"{self.start_date:%-d %B} \u2013 {self.end_date:%-d %B %Y}"

    @property
    def past(self):
        return self.end_date < datetime.date.today()

    @property
    def inline_cta(self):
        return self.call_to_action

    def get_series_events(self):
        today = datetime.date.today()
        query = (
            EventDetailPage.objects.filter(series=self.series)
            .not_page(self)
            .live()
            .order_by("start_date")
            .select_related("hero_image", "listing_image")
        )
        events = []

        def map_data(events):
            return [
                {
                    "title": e.title,
                    "link": e.url,
                    "meta": "",  # TODO: on separate ticket
                    "description": e.introduction,
                    "image": e.listing_image if e.listing_image else e.hero_image,
                }
                for e in events
            ]

        for date_filter in (
            models.Q(start_date__gte=today),
            models.Q(start_date__lt=today),
        ):
            events.extend(map_data(query.filter(date_filter)))

        return events

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update(
            hero_image=self.hero_image,
            series_events=self.get_series_events() if self.series else [],
        )
        return context
