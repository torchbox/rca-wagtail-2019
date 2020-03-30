from collections import defaultdict

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from rca.shortcourses.access_planit import AccessPlanitXML
from rca.utils.blocks import AccordionBlockWithTitle
from rca.utils.models import BasePage


class ShortCoursePage(BasePage):
    parent_page_types = ["programmes.ProgrammeIndexPage"]
    template = "patterns/pages/shortcourses/short_course.html"

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

    access_planit_course_id = models.CharField(max_length=10)
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
    content_panels = BasePage.content_panels + [
        MultiFieldPanel([ImageChooserPanel("hero_image")], heading=_("Hero")),
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

    def get_access_planit_data(self):
        data = AccessPlanitXML(course_id=self.access_planit_course_id)
        return data.get_data()

    def _format_booking_bar(self, access_planit_data, register_interest_link):
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
        if self.access_planit_course_id:
            booking_bar["link"] = register_interest_link

        if access_planit_data:
            for date in access_planit_data:
                if date["status"] == "Available":
                    booking_bar["message"] = "Next course starts"
                    booking_bar["date"] = date["start_date"]
                    booking_bar["action"] = f"Book now from \xA3{date['cost']}"
                    booking_bar["link"] = None
                    booking_bar["modal"] = "booking-details"
                    break
        return booking_bar

    def clean(self):
        errors = defaultdict(list)
        try:
            int(self.access_planit_course_id)
        except ValueError:
            errors["access_planit_course_id"].append(
                "Please enter a valid course id in the form of a number, E.G 731014"
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
        ) = "{settings.ACCESS_PLANIT_REGISTER_INTEREST_BASE}/?course_id={self.access_planit_course_id}"
        context["booking_bar"] = self._format_booking_bar(
            access_planit_data, register_interest_link
        )
        context["access_planit_data"] = access_planit_data
        return context
