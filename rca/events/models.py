import datetime
from urllib.parse import urlencode

from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
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

from rca.events.utils import get_linked_taxonomy
from rca.people.filter import SchoolCentreDirectorateFilter
from rca.people.models import Directorate
from rca.research.models import ResearchCentrePage
from rca.schools.models import SchoolPage
from rca.utils.filter import TabStyleFilter
from rca.utils.models import (
    BasePage,
    ContactFieldsMixin,
    RelatedPage,
    RelatedStaffPageWithManualOptions,
)

from .blocks import CallToAction, EventDetailPageBlock, PartnersBlock
from .forms import EventAdminForm


class EventIndexPageRelatedEditorialPage(Orderable):
    page = models.ForeignKey(
        "events.EventDetailPage",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="+",
    )
    source_page = ParentalKey("EventIndexPage", related_name="related_event_pages")
    panels = [PageChooserPanel("page")]


class EventIndexPage(ContactFieldsMixin, BasePage):
    base_form_class = EventAdminForm
    subpage_types = ["EventDetailPage"]
    template = "patterns/pages/events/event_listing.html"

    class Meta:
        verbose_name = "Event Listing Page"

    introduction = models.CharField(max_length=200, blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        MultiFieldPanel(
            [InlinePanel("related_event_pages", max_num=6, label="Event Pages")],
            heading="Editors picks",
        ),
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

    def get_editor_picks(self):
        related_pages = []
        pages = (
            self.related_event_pages.all()
            .prefetch_related("page__hero_image", "page__listing_image")
            .filter(page__live=True)
        )
        for value in pages:
            page = value.page
            if page:
                meta = page.event_type
                if page.location:
                    description = f"{page.event_date_short}, {page.location}"
                else:
                    description = f"{page.event_date_short}"

                related_pages.append(
                    {
                        "title": page.title,
                        "link": page.url,
                        "image": page.listing_image or page.hero_image,
                        "description": description,
                        "meta": meta,
                    }
                )
        return related_pages

    def get_base_queryset(self):
        return EventDetailPage.objects.child_of(self).live().order_by("-start_date")

    def modify_results(self, paginator_page, request):
        for obj in paginator_page.object_list:
            if obj.location:
                date = f"{obj.event_date_short}, {obj.location}"
            else:
                date = f"{obj.event_date_short}"

            obj.link = obj.get_url(request)
            obj.image = obj.listing_image or obj.hero_image
            obj.short_date = date
            obj.title = obj.listing_title or obj.title
            if obj.event_type:
                obj.type = obj.event_type

    def get_active_filters(self, request):
        return {
            "type": request.GET.getlist("type"),
            "series": request.GET.getlist("series"),
            "location": request.GET.getlist("location"),
            "eligibility": request.GET.getlist("eligibility"),
            "school_or_centre": request.GET.getlist("school-centre-or-area"),
        }

    def get_extra_query_params(self, request, active_filters):
        extra_query_params = []
        for filter_name in active_filters:
            for filter_id in active_filters[filter_name]:
                extra_query_params.append(urlencode({filter_name: filter_id}))
        return extra_query_params

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["featured_editorial"] = self.get_editor_picks()

        base_queryset = self.get_base_queryset()
        queryset = base_queryset.all()

        filters = (
            SchoolCentreDirectorateFilter(
                "School, Centre or Area",
                school_queryset=SchoolPage.objects.live().filter(
                    id__in=base_queryset.values_list(
                        "related_schools__page_id", flat=True
                    )
                ),
                centre_queryset=ResearchCentrePage.objects.live().filter(
                    id__in=base_queryset.values_list(
                        "related_research_centre_pages__page_id", flat=True
                    )
                ),
                directorate_queryset=Directorate.objects.filter(
                    id__in=base_queryset.values_list(
                        "related_directorates__directorate_id", flat=True
                    )
                ),
            ),
            TabStyleFilter(
                "Type",
                queryset=(
                    EventType.objects.filter(
                        id__in=base_queryset.values_list("event_type_id", flat=True)
                    )
                ),
                filter_by="event_type__slug__in",  # Filter by slug here
                option_value_field="slug",
            ),
            TabStyleFilter(
                "Location",
                queryset=(
                    EventLocation.objects.filter(
                        id__in=base_queryset.values_list("location_id", flat=True)
                    )
                ),
                filter_by="location__slug__in",  # Filter by slug here
                option_value_field="slug",
            ),
            TabStyleFilter(
                "Who can attend",
                queryset=(
                    EventEligibility.objects.filter(
                        id__in=base_queryset.values_list("eligibility_id", flat=True)
                    )
                ),
                filter_by="eligibility__slug__in",  # Filter by slug here
                option_value_field="slug",
            ),
            TabStyleFilter(
                "Series",
                queryset=(
                    EventSeries.objects.filter(
                        id__in=base_queryset.values_list("series_id", flat=True)
                    )
                ),
                filter_by="series__slug__in",  # Filter by slug here
                option_value_field="slug",
            ),
        )

        # Apply filters
        for f in filters:
            queryset = f.apply(queryset, request.GET)

        # Paginate filtered queryset
        per_page = 12
        page_number = request.GET.get("page")
        paginator = Paginator(queryset, per_page)
        try:
            results = paginator.page(page_number)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        # Set additional attributes etc
        self.modify_results(results, request)

        # Finalise and return context
        context.update(
            filters={
                "title": "Filter by",
                "aria_label": "Filter results",
                "items": filters,
            },
            results=results,
            result_count=paginator.count,
        )

        context["show_picks"] = True
        extra_query_params = self.get_extra_query_params(
            request, self.get_active_filters(request)
        )
        if extra_query_params or (page_number and page_number != "1"):
            context["show_picks"] = False

        return context


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


class EventSeries(EventTaxonomyBase):
    title = models.CharField(max_length=128)
    introduction = models.TextField()

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title

    panels = [FieldPanel("title"), FieldPanel("introduction")]


class EventDetailPageSpeaker(RelatedStaffPageWithManualOptions):
    source_page = ParentalKey("events.EventDetailPage", related_name="speakers")


class EventDetailPageRelatedDirectorate(Orderable):
    source_page = ParentalKey(
        "events.EventDetailPage", related_name="related_directorates"
    )
    directorate = models.ForeignKey(
        "people.Directorate", on_delete=models.CASCADE, related_name="+",
    )
    panels = [FieldPanel("directorate")]

    class Meta:
        ordering = ["sort_order"]


class EventDetailPageRelatedPages(RelatedPage):
    source_page = ParentalKey("events.EventDetailPage", related_name="related_pages")

    panels = [
        PageChooserPanel(
            "page",
            [
                "events.EventDetailPage",
                "guides.GuidePage",
                "programmes.ProgrammePage",
                "schools.SchoolPage",
                "research.ResearchCentrePage",
                "shortcourses.ShortCoursePage",
                "editorial.EditorialPage",
                "landingpages.InnovationLandingPage",
                "landingpages.EELandingPage",
                "landingpages.ResearchLandingPage",
                "landingpages.EnterpriseLandingPage",
            ],
        )
    ]


class EventDetailPage(ContactFieldsMixin, BasePage):
    base_form_class = EventAdminForm
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
        InlinePanel(
            "related_directorates", heading="Directorates", label="Directorate"
        ),
        InlinePanel(
            "related_research_centre_pages",
            heading="Research Centres",
            label="Research Centre",
        ),
        InlinePanel("related_schools", heading="Schools", label="School"),
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
        InlinePanel(
            "related_pages", label="Page", heading="Also of interest", max_num=6
        ),
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

    def get_related_pages(self):
        related_pages = {"title": "Also of interest", "items": []}
        pages = self.related_pages.all()
        for value in pages:
            page = value.page.specific
            if not page.live:
                continue

            meta = ""
            if (
                page.__class__.__name__ == "EditorialPage"
                and page.editorial_types.first()
            ):
                meta = page.editorial_types.first().type
            elif page.__class__.__name__ == "EventDetailPage":
                meta = "Event"
            elif page.__class__.__name__ == "GuidePage":
                meta = "Guide"
            elif page.__class__.__name__ == "ProgrammePage":
                meta = "Programme"
            elif page.__class__.__name__ == "ResearchCentrePage":
                meta = "Research Centre"
            elif page.__class__.__name__ == "SchoolPage":
                meta = "School"
            elif page.__class__.__name__ == "ShortCoursePage":
                meta = "Short Course"

            if hasattr(page, "hero_image") and page.hero_image:
                hero_image = page.hero_image

            if hasattr(page, "introduction"):
                description = page.introduction

            related_pages["items"].append(
                {
                    "title": page.listing_title or page.title,
                    "link": page.url,
                    "image": page.listing_image or hero_image,
                    "description": page.listing_summary or description,
                    "meta": meta,
                }
            )
        return related_pages

    @property
    def event_date(self):
        if self.start_date == self.end_date:
            return f"{self.end_date:%-d %B %Y}"
        return f"{self.start_date:%-d %B} \u2013 {self.end_date:%-d %B %Y}"

    @property
    def event_date_short(self):
        """Method to return a specific date format
        1) When a single date:
            E.G. 13 May 2021
            E.G. 9 May 2021
            (NB - no ordinals, no '0' before single digit dates).

        2) When a span within a month:
            E.G. 13–15 May 2021
            (NB closed en-dash for date range)

        3) When a span across multiple months:
            E.G.13 May – 15 June 2021
            (NB spaced en-dash)

        4) When a span across multiple years:
            E.G. 13 December 2021 – 13 January 2022.
        """
        start_date_month = self.start_date.strftime("%B")
        start_date_year = self.start_date.strftime("%Y")
        end_date_month = self.end_date.strftime("%B")
        end_date_year = self.end_date.strftime("%Y")

        start_date = self.start_date.strftime("%-d %B %Y")
        end_date = self.end_date.strftime("%-d %B %Y")

        if start_date == end_date:
            # 1 Single day
            # E.G 20 July 2021
            return start_date
        elif end_date_year != start_date_year:
            # 4 When a span across multiple years:
            # E.G. 13 December 2021 – 13 January 2022.
            return f"{str(self.start_date.strftime('%-d %B %Y'))} - {str(self.end_date.strftime('%-d %B %Y'))}"
        elif start_date_month == end_date_month:
            # 2 Same month, different days
            # E.G 20 - 22nd July 2021
            return f"{str(self.start_date.strftime('%-d'))} - {str(self.end_date.strftime('%-d %B %Y'))}"
        else:
            # 3 Multiple month span
            # E.G 20th June - 22nd July 2021
            return f"{str(self.start_date.strftime('%-d %B'))} - {str(self.end_date.strftime('%-d %B %Y'))}"

    @property
    def past(self):
        return self.end_date < datetime.date.today()

    @property
    def inline_cta(self):
        return self.call_to_action

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        if self.show_booking_bar and not all(
            [
                self.manual_registration_url_link_text,
                self.manual_registration_url,
                self.event_cost,
                self.availability,
                self.location,
            ]
        ):
            raise ValidationError(
                {"show_booking_bar": "Please complete all booking fields."}
            )

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

    def get_booking_bar(self):
        return {
            "action": self.manual_registration_url_link_text,
            "link": self.manual_registration_url,
            "message": " | ".join(
                [
                    self.event_cost,
                    self.location.title if self.location else "",
                    self.availability.title if self.availability else "",
                ]
            ),
        }

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update(
            booking_bar=self.get_booking_bar() if self.show_booking_bar else {},
            hero_image=self.hero_image,
            series_events=self.get_series_events() if self.series else [],
            speakers=self.speakers.all,
            taxonomy_tags=get_linked_taxonomy(self, request),
            related_pages=self.get_related_pages(),
        )
        return context
