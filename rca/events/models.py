import datetime
import itertools

from django.db import models
from django.db.models.fields import SlugField
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from rca.utils.models import (
    BasePage,
    ContactFieldsMixin,
    RelatedStaffPageWithManualOptions,
)

from .blocks import CallToAction, EventDetailPageBlock, PartnersBlock
from .forms import EventPageAdminForm


class EventIndexPage(BasePage):
    subpage_types = ["EventDetailPage"]
    template = "patterns/pages/events/event_index_page.html"

    # TODO: add fields to this placeholder model (needed as event detail parent)


class EventTaxonomyBase(models.Model):
    title = models.CharField(max_length=100)
    slug = SlugField()

    class Meta:
        abstract = True
        ordering = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    panels = [FieldPanel("title")]


class EventAvailability(EventTaxonomyBase):
    pass


class EventEligibility(EventTaxonomyBase):
    pass


class EventLocation(EventTaxonomyBase):
    pass


class EventType(EventTaxonomyBase):
    pass


class EventSeries(models.Model):
    title = models.CharField(max_length=128)
    introduction = models.TextField()

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class EventDetailPageSpeaker(RelatedStaffPageWithManualOptions):
    source_page = ParentalKey("events.EventDetailPage", related_name="speakers")


class EventDetailPageRelatedDirectorate(Orderable):
    source_page = ParentalKey("events.EventDetailPage", related_name="directorates")
    directorate = models.ForeignKey(
        "people.Directorate", on_delete=models.CASCADE, related_name="+",
    )
    panels = [FieldPanel("directorate")]

    class Meta:
        ordering = ["sort_order"]


class EventDetailPageRelatedResearchCentre(Orderable):
    source_page = ParentalKey("events.EventDetailPage", related_name="research_centres")
    research_centre = models.ForeignKey(
        "research.ResearchCentrePage", on_delete=models.CASCADE, related_name="+",
    )
    panels = [PageChooserPanel("research_centre")]

    class Meta:
        ordering = ["sort_order"]


class EventDetailPageRelatedSchool(Orderable):
    source_page = ParentalKey("events.EventDetailPage", related_name="schools")
    school = models.ForeignKey(
        "schools.SchoolPage", on_delete=models.CASCADE, related_name="+",
    )
    panels = [PageChooserPanel("school")]

    class Meta:
        ordering = ["sort_order"]


class EventDetailPage(ContactFieldsMixin, BasePage):
    base_form_class = EventPageAdminForm
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
    speaker_heading = models.CharField(
        blank=True, max_length=120, verbose_name="Heading"
    )
    partners_heading = models.CharField(
        blank=True, max_length=120, verbose_name="Heading"
    )
    partners = StreamField(PartnersBlock(required=False), blank=True)
    call_to_action = StreamField(CallToAction(required=False), blank=True)
    # booking bar
    show_booking_bar = models.BooleanField(default=False)
    manual_registration_url_link_text = models.CharField(
        blank=True, max_length=50, verbose_name="Booking URL link text",
    )
    manual_registration_url = models.URLField(
        blank=True, max_length=255, verbose_name="Booking URL",
    )
    event_cost = models.CharField(blank=True, max_length=50, verbose_name="Cost")
    availability = models.ForeignKey(
        EventAvailability,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="events",
    )
    location = models.ForeignKey(
        EventLocation,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="events",
    )

    content_panels = BasePage.content_panels + [
        ImageChooserPanel("hero_image"),
        MultiFieldPanel(
            [FieldPanel("start_date"), FieldPanel("end_date")], heading="Event Dates",
        ),
        MultiFieldPanel(
            [
                FieldPanel("show_booking_bar"),
                FieldPanel("manual_registration_url_link_text"),
                FieldPanel("manual_registration_url"),
                FieldPanel("event_cost"),
                FieldPanel("availability"),
                FieldPanel("location"),
            ],
            heading="Event Booking",
        ),
        MultiFieldPanel(
            [FieldPanel("event_type"), FieldPanel("series"), FieldPanel("eligibility")],
            heading="Event Taxonomy",
        ),
        InlinePanel("directorates", heading="Directorates", label="Directorate"),
        InlinePanel(
            "research_centres", heading="Research Centres", label="Research Centre"
        ),
        InlinePanel("schools", heading="Schools", label="School"),
        FieldPanel("introduction"),
        StreamFieldPanel("body"),
        MultiFieldPanel(
            [FieldPanel("speaker_heading"), InlinePanel("speakers")],
            heading=_("Event Speakers"),
        ),
        MultiFieldPanel(
            [FieldPanel("partners_heading"), StreamFieldPanel("partners")],
            heading="Partners",
        ),
        StreamFieldPanel("call_to_action"),
        MultiFieldPanel(
            [
                FieldPanel("contact_model_title"),
                FieldPanel("contact_model_email"),
                FieldPanel("contact_model_url"),
                PageChooserPanel("contact_model_form"),
                FieldPanel("contact_model_link_text"),
                FieldPanel("contact_model_text"),
                ImageChooserPanel("contact_model_image"),
            ],
            "Large Call To Action",
        ),
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

    def get_taxonomy_tags(self):
        directorates = [
            {"title": d.directorate.title, "href": "#"}  # TODO: href on separate ticket
            for d in self.directorates.select_related("directorate")
        ]
        schools = [
            {"title": p.school.title, "href": "#"}  # TODO: href on separate ticket
            for p in self.schools.all().select_related("school")
            if p.school.live  # inefficient hack because modelcluster doesn't support filter lookup
        ]
        research_centres = [
            {
                "title": p.research_centre.title,
                "href": "#",  # TODO: href on separate ticket
            }
            for p in self.research_centres.all().select_related("research_centre")
            if p.research_centre.live  # inefficient hack because modelcluster doesn't support filter lookup
        ]

        return sorted(
            itertools.chain(directorates, research_centres, schools),
            key=lambda o: o["title"],
        )

    def get_booking_bar(self):
        return {
            "action": self.manual_registration_url_link_text,
            "link": self.manual_registration_url,
            "message": " | ".join(
                [self.event_cost, self.location.title, self.availability.title]
            ),
        }

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update(
            booking_bar=self.get_booking_bar(),
            hero_image=self.hero_image,
            series_events=self.get_series_events() if self.series else [],
            speakers=self.speakers.all,
            taxonomy_tags=self.get_taxonomy_tags(),
        )
        return context
