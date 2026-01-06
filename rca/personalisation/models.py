from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.models import Orderable, PreviewableMixin
from wagtail_personalisation.models import Segment

"""
We cannot set a custom form on InlinePanels to dynamically update
the list of page types (if/when we add more) so we just hard code
the list of page types here. The choices can be retrieved by doing
the following:

>   def get_all_subclasses(cls):
        all_subclasses = []
        for subclass in cls.__subclasses__():
            all_subclasses.append(subclass)
            all_subclasses.extend(get_all_subclasses(subclass))
            return all_subclasses
>   get_all_subclasses(BasePage)
"""
PAGE_TYPE_CHOICES = [
    ("home.homepage", "Home Page"),
    ("programmes.programmepage", "Programme Page"),
    ("programmes.programmeindexpage", "Programme Index Page"),
    ("events.eventdetailpage", "Event Detail Page"),
    ("events.eventindexpage", "Event Index Page"),
    ("editorial.editorialpage", "Editorial Page"),
    ("editorial.editoriallistingpage", "Editorial Listing Page"),
    ("guides.guidepage", "Guide Page"),
    ("projects.projectpage", "Project Page"),
    ("projects.projectpickerpage", "Project Picker Page"),
    ("research.researchcentrepage", "Research Centre Page"),  #
    ("schools.schoolpage", "School Page"),  #
    ("people.staffpage", "Staff Page"),
    ("people.studentpage", "Student Page"),
    ("people.staffindexpage", "Staff Index Page"),
    ("people.studentindexpage", "Student Index Page"),
    ("shortcourses.shortcoursepage", "Short Course Page"),
    ("landingpages.landingpage", "Landing Page"),
    ("landingpages.alumnilandingpage", "Alumni Landing Page"),
    ("landingpages.developmentlandingpage", "Development Landing Page"),
    ("landingpages.enterpriselandingpage", "Enterprise Landing Page"),
    ("landingpages.innovationlandingpage", "Innovation Landing Page"),
    ("landingpages.researchlandingpage", "Research Landing Page"),
    ("landingpages.taplandingpage", "Tap Landing Page"),
    ("landingpages.eelandingpage", "EE Landing Page"),
    ("standardpages.informationpage", "Information Page"),
    ("standardpages.indexpage", "Index Page"),
    ("forms.formpage", "Form Page"),
    ("donate.donationformpage", "Donation Form Page"),
    ("scholarships.scholarshipslistingpage", "Scholarships Listing Page"),
]


class UserActionCTASegment(Orderable):
    """This links a personalised CTA to a segment"""

    segment = models.ForeignKey(
        Segment, related_name="personalised_call_to_actions", on_delete=models.CASCADE
    )
    call_to_action = ParentalKey(
        "personalisation.UserActionCallToAction", related_name="segments"
    )

    class Meta:
        unique_together = ("segment", "call_to_action")

    panels = [
        FieldPanel("segment"),
    ]


class UserActionCTAPageType(Orderable):
    """
    This links a CTA to a page type so we know which page types to apply the CTA to.
    """

    page_type = models.CharField(
        max_length=100,
        choices=PAGE_TYPE_CHOICES,
        help_text="Select the page type where this CTA should appear",
    )
    call_to_action = ParentalKey(
        "personalisation.UserActionCallToAction", related_name="page_types"
    )

    class Meta:
        unique_together = ("page_type", "call_to_action")

    panels = [
        FieldPanel("page_type"),
    ]

    def __str__(self):
        return self.get_page_type_display()


class UserActionCallToAction(PreviewableMixin, ClusterableModel):
    USER_ACTION_CHOICES = [
        ("page_load", "On page load"),
        ("inactivity", "On inactivity after X seconds"),
        ("scroll", "On scroll after X% of the way down"),
        ("exit_intent", "On exit intent"),
    ]

    # Required fields
    image = models.ForeignKey(
        "images.CustomImage",
        on_delete=models.CASCADE,
        related_name="+",
    )
    title = models.CharField(max_length=40)
    description = models.CharField(max_length=65)

    # Link fields (either internal or external)
    internal_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Link to an internal page",
    )
    external_link = models.URLField(
        blank=True,
        help_text="Link to an external URL (e.g., https://example.com)",
    )
    link_label = models.CharField(
        max_length=40,
        blank=True,
        help_text=(
            "Maximum 40 characters for the link button text. "
            "If using an internal link, leave blank to use the page's title."
        ),
    )

    # User action condition
    user_action = models.CharField(
        max_length=20,
        choices=USER_ACTION_CHOICES,
        default="page_load",
        help_text="Choose when this CTA should appear",
    )
    inactivity_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of seconds of inactivity before showing the CTA (only for 'On inactivity')",
    )
    scroll_percentage = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Percentage of page scrolled before showing the CTA (only for 'On scroll', e.g., 50 for 50%)",
    )

    # Scheduling
    go_live_at = models.DateTimeField(
        verbose_name="Go live date/time",
        blank=True,
        null=True,
        help_text="The date and time when this CTA should start appearing.",
    )
    expire_at = models.DateTimeField(
        verbose_name="Expiry date/time",
        blank=True,
        null=True,
        help_text="The date and time when this CTA should stop appearing.",
    )

    class Meta:
        verbose_name = "User Action Pop-up CTA"
        verbose_name_plural = "User Action Pop-up CTAs"

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("image"),
                FieldPanel("title"),
                FieldPanel("description"),
                MultiFieldPanel(
                    [
                        PageChooserPanel("internal_link"),
                        FieldPanel("external_link"),
                        FieldPanel("link_label"),
                    ],
                    heading="Link (choose either internal or external)",
                ),
            ],
            heading="Content",
        ),
        MultiFieldPanel(
            [
                FieldPanel("user_action"),
                FieldPanel("inactivity_seconds"),
                FieldPanel("scroll_percentage"),
            ],
            heading="User Action Condition",
        ),
        InlinePanel(
            "segments",
            label="Segments",
            heading="Segments",
            help_text=(
                "Select the segments that must apply for this CTA to appear. "
                "You may select multiple segments. "
                "If no segments are selected, the CTA will not appear. "
                "If multiple segments are selected, the CTA will appear when at least "
                "one of the selected segments applies."
            ),
        ),
        InlinePanel(
            "page_types",
            label="Page Types",
            heading="Page Types",
            help_text="Select the page types where this CTA should appear.",
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("go_live_at"),
                        FieldPanel("expire_at"),
                    ]
                )
            ],
            heading="Scheduling",
            help_text=(
                "When the CTA should appear/expire. Leave blank to disable the CTA."
            ),
        ),
    ]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        errors = {}

        # Validate link fields
        if self.internal_link and self.external_link:
            errors["internal_link"] = (
                "Please choose either an internal link or an external link, not both"
            )
            errors["external_link"] = (
                "Please choose either an internal link or an external link, not both"
            )
        elif not self.internal_link and not self.external_link:
            errors["internal_link"] = (
                "Please provide either an internal link or an external link"
            )
            errors["external_link"] = (
                "Please provide either an internal link or an external link"
            )

        if self.external_link and not self.link_label:
            errors["link_label"] = (
                "If using an external link, please provide the link button text"
            )

        # Validate user action parameters
        if self.user_action == "inactivity":
            if not self.inactivity_seconds:
                errors["inactivity_seconds"] = (
                    "Please specify the number of seconds of inactivity"
                )
            elif self.inactivity_seconds <= 0:
                errors["inactivity_seconds"] = (
                    "Inactivity seconds must be greater than 0"
                )

        if self.user_action == "scroll":
            if not self.scroll_percentage:
                errors["scroll_percentage"] = "Please specify the scroll percentage"
            elif self.scroll_percentage <= 0 or self.scroll_percentage > 100:
                errors["scroll_percentage"] = (
                    "Scroll percentage must be between 1 and 100"
                )

        # Validate dates
        now = timezone.now()

        if self.go_live_at and self.go_live_at < now:
            errors["go_live_at"] = "Go live date/time cannot be in the past"

        if self.expire_at and self.expire_at < now:
            errors["expire_at"] = "Expiry date/time cannot be in the past"

        if self.go_live_at and self.expire_at and self.expire_at <= self.go_live_at:
            errors["expire_at"] = "Expiry date/time must be after go live date/time"

        if errors:
            raise ValidationError(errors)

    def get_preview_template(self, request, mode_name):
        return "patterns/molecules/cta_modal/cta_modal.html"

    def get_preview_context(self, request, mode_name):
        context = super().get_preview_context(request, mode_name)
        context["value"] = {
            "image": self.image,
            "title": self.title,
            "description": self.description,
            "href": self.external_link or self.internal_link.url,
            "text": self.link_label
            or (self.internal_link.title if self.internal_link else None),
        }
        return context
