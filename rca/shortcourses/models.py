from collections import defaultdict

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from rest_framework.fields import CharField as CharFieldSerializer
from wagtail.admin.edit_handlers import (
    FieldPanel,
    HelpPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.api import APIField
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable
from wagtail.images import get_image_model_string
from wagtail.images.api.fields import ImageRenditionField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from rca.programmes.models import ProgrammeType
from rca.shortcourses.access_planit import AccessPlanitXML
from rca.utils.blocks import (
    AccordionBlockWithTitle,
    GalleryBlock,
    LinkBlock,
    QuoteBlock,
)
from rca.utils.models import (
    HERO_COLOUR_CHOICES,
    BasePage,
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


class ShortCourseManualDate(Orderable):
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    booking_link = models.URLField(blank=True, null=True)
    register_interest_link = models.URLField(blank=True, null=True)
    cost = models.PositiveIntegerField(blank=True, null=True)
    source_page = ParentalKey("ShortCoursePage", related_name="manual_bookings")
    panels = [
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        FieldPanel("booking_link"),
        FieldPanel("register_interest_link"),
        FieldPanel("cost"),
    ]

    def clean(self):
        errors = defaultdict(list)
        super().clean()

        if self.register_interest_link and self.booking_link:
            errors["booking_link"].append(_("Please define only one link."))

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


class ShortCoursePage(BasePage):
    template = "patterns/pages/shortcourses/short_course.html"

    hero_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_colour_option = models.PositiveSmallIntegerField(choices=(HERO_COLOUR_CHOICES))
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

    access_planit_course_id = models.IntegerField()
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
        help_text="If selected, an automatic 'Register your interest' link will be \
                                                                   visible in the key details section",
    )
    course_details_text = RichTextField(blank=True)
    programme_type = models.ForeignKey(
        ProgrammeType,
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name="+",
    )
    location = RichTextField(blank=True, features=["link"])
    introduction = models.CharField(max_length=500, blank=True)

    quote_carousel = StreamField(
        [("quote", QuoteBlock())], blank=True, verbose_name=_("Quote carousel")
    )
    staff_title = models.CharField(
        max_length=50,
        blank=True,
        help_text="Heading to display above the short course team members, E.G Programme Team",
    )
    gallery = StreamField(
        [("slide", GalleryBlock())], blank=True, verbose_name="Gallery"
    )
    contact_email = models.EmailField(blank=True)
    contact_url = models.URLField(blank=True)
    contact_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    contact_text = models.TextField(blank=True)
    external_links = StreamField(
        [("link", LinkBlock())], blank=True, verbose_name="External Links"
    )
    application_form_url = models.URLField(
        blank=True,
        help_text="Adding an application form URL will override the booking link to Access Planit",
    )
    manual_registration_url = models.URLField(
        blank=True, help_text="Override the register interest link show in the modal",
    )

    access_planit_and_course_data_panels = [
        MultiFieldPanel(
            [
                FieldPanel("manual_registration_url"),
                HelpPanel(
                    "Defining course details manually will override any Access Planit data configured for this page"
                ),
                InlinePanel("manual_bookings", label="Booking"),
            ],
            heading="Manual course configuration",
        ),
        MultiFieldPanel(
            [FieldPanel("application_form_url")], heading="Application URL"
        ),
        FieldPanel("access_planit_course_id"),
        MultiFieldPanel(
            [
                FieldPanel("course_details_text"),
                SnippetChooserPanel("frequently_asked_questions"),
                SnippetChooserPanel("terms_and_conditions"),
            ],
            heading="course details",
        ),
    ]
    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [ImageChooserPanel("hero_image"), FieldPanel("hero_colour_option")],
            heading=_("Hero"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("introduction"),
                ImageChooserPanel("introduction_image"),
                FieldPanel("video"),
                FieldPanel("video_caption"),
                FieldPanel("body"),
            ],
            heading=_("Course Introduction"),
        ),
        StreamFieldPanel("about"),
        FieldPanel("programme_type"),
        StreamFieldPanel("quote_carousel"),
        MultiFieldPanel(
            [FieldPanel("staff_title"), InlinePanel("related_staff", label="Staff")],
            heading="Short course team",
        ),
        StreamFieldPanel("gallery"),
        MultiFieldPanel(
            [
                ImageChooserPanel("contact_image"),
                FieldPanel("contact_text"),
                FieldPanel("contact_url"),
                FieldPanel("contact_email"),
            ],
            heading="Contact information",
        ),
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
        StreamFieldPanel("external_links"),
    ]
    key_details_panels = [
        InlinePanel("fee_items", label="Fees"),
        FieldPanel("location"),
        FieldPanel("show_register_link"),
        InlinePanel("subjects", label=_("Subjects")),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(
                access_planit_and_course_data_panels, heading="Course configuration"
            ),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
        ]
    )

    search_fields = BasePage.search_fields + [
        index.SearchField("introduction", partial_match=True),
        index.AutocompleteField("introduction", partial_match=True),
        index.RelatedFields(
            "programme_type",
            [
                index.SearchField("display_name", partial_match=True),
                index.AutocompleteField("display_name", partial_match=True),
            ],
        ),
        index.RelatedFields(
            "subjects",
            [
                index.RelatedFields(
                    "subject",
                    [
                        index.SearchField("title", partial_match=True),
                        index.AutocompleteField("title", partial_match=True),
                    ],
                )
            ],
        ),
    ]

    api_fields = [
        # Fields for filtering and display, shared with programmes.ProgrammePage.
        APIField("subjects"),
        APIField("programme_type"),
        APIField("related_schools_and_research_pages"),
        APIField("summary", serializer=CharFieldSerializer(source="introduction")),
        APIField(
            name="hero_image_square",
            serializer=ImageRenditionField("fill-580x580", source="hero_image"),
        ),
    ]

    @property
    def get_manual_bookings(self):
        return self.manual_bookings.all()

    def get_access_planit_data(self):
        access_planit_course_data = AccessPlanitXML(
            course_id=self.access_planit_course_id
        )
        return access_planit_course_data.get_data()

    def _format_booking_bar(self, register_interest_link=None, access_planit_data=None):
        """ Booking bar messaging with the next course data available
        Find the next course date marked as status='available' and advertise
        this date in the booking bar. If there are no courses available, add
        a default message."""

        booking_bar = {
            "message": "Applications are now closed",
            "action": "Register your interest for upcoming dates",
        }
        # If there are no dates the booking link should go to a form, not open
        # a modal, this link is also used as a generic interest link too though.
        booking_bar["link"] = register_interest_link

        # If manual_booking links are defined, format the booking bar and return
        # it before checking access planit
        if self.manual_bookings.first():
            date = self.manual_bookings.first()
            booking_bar["message"] = "Next course starts"
            booking_bar["date"] = date.start_date
            if date.booking_link:
                booking_bar["action"] = (
                    f"Book from \xA3{date.cost}" if date.cost else f"Book now"
                )
            if date.register_interest_link:
                booking_bar["action"] = "Register your interest"
            booking_bar["modal"] = "booking-details"
            booking_bar["cost"] = date.cost
            return booking_bar

        # If there is access planit data, format the booking bar
        if access_planit_data:
            for date in access_planit_data:
                if date["status"] == "Available":
                    booking_bar["message"] = "Next course starts"
                    booking_bar["date"] = date["start_date"]
                    booking_bar["action"] = (
                        "Submit form to apply"
                        if self.application_form_url
                        else f"Book now from \xA3{date['cost']}"
                    )
                    booking_bar["cost"] = date["cost"]
                    booking_bar["link"] = None
                    booking_bar["modal"] = "booking-details"
                    break
            return booking_bar

        return booking_bar

    def clean(self):
        errors = defaultdict(list)
        if not self.contact_email and not self.contact_url:
            errors["contact_url"].append(
                "Please add a target value for the contact us link"
            )
        if self.contact_email and self.contact_url:
            errors["contact_url"].append(
                "Only one of URL or an Email value is supported here"
            )
        if errors:
            raise ValidationError(errors)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        access_planit_data = self.get_access_planit_data()
        context[
            "register_interest_link"
        ] = (
            register_interest_link
        ) = f"{settings.ACCESS_PLANIT_REGISTER_INTEREST_BASE}?course_id={self.access_planit_course_id}"
        context["booking_bar"] = self._format_booking_bar(
            register_interest_link, access_planit_data
        )
        context["booking_bar"] = self._format_booking_bar(
            register_interest_link, access_planit_data
        )
        context["access_planit_data"] = access_planit_data
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
