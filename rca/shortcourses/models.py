from collections import defaultdict

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from rest_framework.fields import CharField as CharFieldSerializer
from taggit.models import TaggedItemBase
from wagtail.admin.panels import (
    FieldPanel,
    HelpPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.images.api.fields import ImageRenditionField
from wagtail.models import Orderable
from wagtail.search import index

from rca.utils.blocks import (
    AccordionBlockWithTitle,
    GalleryBlock,
    LinkBlock,
    QuoteBlock,
)
from rca.utils.models import (
    BasePage,
    ContactFieldsMixin,
    RelatedPage,
    RelatedStaffPageWithManualOptions,
)


class FeeItem(models.Model):
    source_page = ParentalKey("ShortCoursePage", related_name="fee_items")
    text = models.CharField(max_length=128)
    panel = [FieldPanel("text")]

    def __str__(self):
        return self.text


class ShortCourseRelatedStaff(RelatedStaffPageWithManualOptions):
    source_page = ParentalKey(
        "shortcourses.ShortCoursePage", related_name="related_staff"
    )


class ShortCoursePageRelatedProgramme(RelatedPage):
    source_page = ParentalKey(
        "shortcourses.ShortCoursePage", related_name="related_programmes"
    )
    panels = [
        PageChooserPanel(
            "page", ["programmes.ProgrammePage", "shortcourses.ShortCoursePage"]
        )
    ]


class ShortCoursRelatedSchoolsAndResearchPages(RelatedPage):
    source_page = ParentalKey(
        "ShortCoursePage", related_name="related_schools_and_research_pages"
    )
    panels = [
        PageChooserPanel("page", ["schools.SchoolPage", "research.ResearchCentrePage"])
    ]


class ShortCourseSubjectPlacement(models.Model):
    page = ParentalKey("ShortCoursePage", related_name="subjects")
    subject = models.ForeignKey(
        "programmes.Subject", on_delete=models.CASCADE, related_name="short_course"
    )
    panels = [FieldPanel("subject")]


class ShortCourseProgrammeType(models.Model):
    page = ParentalKey("ShortCoursePage", related_name="programme_types")
    programme_type = models.ForeignKey(
        "programmes.ProgrammeType",
        on_delete=models.CASCADE,
        related_name="short_course",
    )
    panels = [FieldPanel("programme_type")]


class ShortCourseManualDate(Orderable):
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    booking_link = models.URLField(blank=True)
    cost = models.PositiveIntegerField(null=True)
    source_page = ParentalKey("ShortCoursePage", related_name="manual_bookings")
    panels = [
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        FieldPanel("booking_link"),
        FieldPanel("cost"),
    ]

    def clean(self):
        errors = defaultdict(list)
        super().clean()

        # Require start time if there's an end time
        if self.end_date:
            if not self.start_date:
                errors["start_date"].append(
                    _("If you enter an end date, you must also enter a start date")
                )

            elif self.end_date < self.start_date:
                errors["end_date"].append(
                    _("Events involving time travel are not supported")
                )

        if errors:
            raise ValidationError(errors)


class ShortCoursePageTag(TaggedItemBase):
    content_object = ParentalKey(
        "shortcourses.ShortCoursePage",
        on_delete=models.CASCADE,
        related_name="tagged_short_course_items",
    )


class ShortCoursePage(ContactFieldsMixin, BasePage):
    template = "patterns/pages/shortcourses/short_course.html"
    parent_page_types = ["programmes.ProgrammeIndexPage"]
    hero_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    introduction = models.CharField(max_length=500, blank=True)
    introduction_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    video_caption = models.CharField(
        blank=True,
        max_length=80,
        help_text="The text dipsplayed next to the video play button",
    )
    video = models.URLField(blank=True)
    body = RichTextField(blank=True)
    about = StreamField(
        [("accordion_block", AccordionBlockWithTitle())],
        blank=True,
        verbose_name=_("About the course"),
    )
    frequently_asked_questions = models.ForeignKey(
        "utils.ShortCourseDetailSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    terms_and_conditions = models.ForeignKey(
        "utils.ShortCourseDetailSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    course_details_text = RichTextField(blank=True)
    show_register_link = models.BooleanField(
        default=1,
        help_text="If selected, an automatic 'Register your interest' link "
        "will be visible in the key details section",
    )
    dates = RichTextField(blank=True, features=["link"])
    location = RichTextField(blank=True, features=["link"])
    introduction = models.CharField(max_length=500, blank=True)

    quote_carousel = StreamField(
        [("quote", QuoteBlock())],
        blank=True,
        verbose_name=_("Quote carousel"),
    )
    staff_title = models.CharField(
        max_length=50,
        blank=True,
        help_text="Heading to display above the short course team members, E.G Programme Team",
    )
    gallery = StreamField(
        [("slide", GalleryBlock())],
        blank=True,
        verbose_name="Gallery",
    )
    external_links = StreamField(
        [("link", LinkBlock())],
        blank=True,
        verbose_name="External Links",
    )
    application_form_url = models.URLField(
        blank=True,
        help_text="The URL of the application form. This will be a direct link and won't open the modal",
    )
    manual_registration_url = models.URLField(
        blank=True,
        help_text="The register interest link shown in the modal",
    )
    tags = ClusterTaggableManager(through=ShortCoursePageTag, blank=True)

    course_data_panels = [
        MultiFieldPanel(
            [
                FieldPanel("manual_registration_url", heading="Registration URL"),
                FieldPanel("application_form_url"),
                InlinePanel("manual_bookings", label="Booking"),
            ],
            heading="Course configuration",
        ),
        MultiFieldPanel(
            [
                FieldPanel("course_details_text"),
                FieldPanel("frequently_asked_questions"),
                FieldPanel("terms_and_conditions"),
            ],
            heading="course details",
        ),
    ]
    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("hero_image")],
            heading=_("Hero"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("introduction"),
                FieldPanel("introduction_image"),
                FieldPanel("video"),
                FieldPanel("video_caption"),
                FieldPanel("body"),
            ],
            heading=_("Course Introduction"),
        ),
        FieldPanel("about"),
        InlinePanel("programme_types", label="Programme types"),
        FieldPanel("quote_carousel"),
        MultiFieldPanel(
            [FieldPanel("staff_title"), InlinePanel("related_staff", label="Staff")],
            heading="Short course team",
        ),
        FieldPanel("gallery"),
        MultiFieldPanel([*ContactFieldsMixin.panels], heading="Contact information"),
        MultiFieldPanel(
            [InlinePanel("related_programmes", label="Related programmes")],
            heading="Related Programmes",
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    "related_schools_and_research_pages",
                    label=_("Related Schools and Research centre pages"),
                )
            ],
            heading=_("Related Schools and Research Centre pages"),
        ),
        FieldPanel("external_links"),
    ]
    key_details_panels = [
        InlinePanel("fee_items", label="Fees"),
        FieldPanel("dates"),
        FieldPanel("location"),
        FieldPanel("show_register_link"),
        InlinePanel("subjects", label=_("Subjects")),
    ]
    promote_panels = BasePage.promote_panels + [
        MultiFieldPanel(
            [
                HelpPanel(
                    content=(
                        "Adding tags will allow users to search for the course "
                        "on the programmes listing page by tags"
                    )
                ),
                FieldPanel("tags"),
            ],
            "Short Course page tags",
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(course_data_panels, heading="Course configuration"),
            ObjectList(promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )

    search_fields = BasePage.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("course_details_text"),
        index.SearchField("body"),
        index.SearchField("about"),
        index.SearchField("location"),
        index.RelatedFields(
            "programme_types",
            [
                index.RelatedFields(
                    "programme_type", [index.SearchField("display_name")]
                )
            ],
        ),
        index.RelatedFields(
            "subjects",
            [index.RelatedFields("subject", [index.SearchField("title")])],
        ),
        index.RelatedFields(
            "tagged_short_course_items",
            [
                index.RelatedFields(
                    "tag",
                    [
                        index.SearchField("name"),
                        index.AutocompleteField("name"),
                    ],
                )
            ],
        ),
    ]

    api_fields = [
        # Fields for filtering and display, shared with programmes.ProgrammePage.
        APIField("subjects"),
        APIField("programme_types"),
        APIField("related_schools_and_research_pages"),
        APIField("summary", serializer=CharFieldSerializer(source="introduction")),
        APIField(
            name="hero_image_square",
            serializer=ImageRenditionField("fill-580x580", source="hero_image"),
        ),
    ]

    @property
    def listing_meta(self):
        # Returns a page 'type' value that's readable for listings,
        return "Short course"

    @property
    def get_manual_bookings(self):
        return self.manual_bookings.all()

    def _format_booking_bar(self):
        """Booking bar messaging with the next course data available
        Find the next course date marked as status='available' and advertise
        this date in the booking bar. If there are no courses available, add
        a default message."""

        booking_bar = {
            "message": "Bookings not yet open",
            "action": "Register your interest for upcoming dates",
            "link": self.manual_registration_url,
        }

        # If manual_booking links are defined, format the booking bar
        manual_booking = self.manual_bookings.first()
        if manual_booking and (
            manual_booking.booking_link or self.application_form_url
        ):
            booking_bar["message"] = "Next course starts"
            booking_bar["date"] = manual_booking.start_date
            booking_bar["action"] = (
                f"Book from \xa3{manual_booking.cost}"
                if manual_booking.cost
                else "Book now"
            )
            booking_bar["modal"] = "booking-details"
            booking_bar["cost"] = manual_booking.cost

            # Override some values if the course has an application form
            if self.application_form_url:
                booking_bar["action"] = "Apply now"
                booking_bar["link"] = self.application_form_url
                booking_bar["modal"] = None

        return booking_bar

    def clean(self):
        super().clean()
        errors = defaultdict(list)
        if self.show_register_link and not self.manual_registration_url:
            errors["show_register_link"].append(
                "A  manual registration link is needed to show the register links"
            )

        if errors:
            raise ValidationError(errors)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context["register_interest_link"] = self.manual_registration_url
        context["booking_bar"] = self._format_booking_bar()
        context["shortcourse_details_fees"] = self.fee_items.values_list(
            "text", flat=True
        )
        context["related_sections"] = [
            {
                "title": "More opportunities to study at the RCA",
                "related_items": [
                    rel.page.specific
                    for rel in self.related_programmes.select_related("page")
                ],
            }
        ]
        context["related_staff"] = self.related_staff.select_related(
            "image"
        ).prefetch_related("page")
        return context

    @property
    def booking_summary(self):
        booking_bar = self._format_booking_bar()

        # If there's no date, the message would say "Bookings are not yet open"
        if booking_date := booking_bar.get("date"):
            return booking_date.strftime("%d %B %Y")

        return booking_bar["message"]
