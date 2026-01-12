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
from wagtail.models import Orderable
from wagtail_personalisation.models import Segment

from rca.personalisation.blocks import CollapsibleNavigationLinkBlock
from rca.utils.fields import StreamField
from rca.utils.mixins import StyledPreviewableMixin

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


class PersonalisedCTAQuerySet(models.QuerySet):
    def for_page_and_segments(self, page_content_type, segments, now):
        """
        Filter CTAs by page type, segments, and time constraints.

        Args:
            page_content_type: String in format "app_label.model_name"
            segments: List/queryset of segments
            now: Current datetime for go_live_at/expire_at checks

        Note:
            At least one of go_live_at or expire_at must be set for the CTA to be active.
            If both are blank, the CTA is considered disabled.
        """
        return self.filter(
            # At least one date must be set (otherwise CTA is disabled)
            models.Q(go_live_at__isnull=False) | models.Q(expire_at__isnull=False),
            # If go_live_at is set, now must be >= go_live_at
            models.Q(go_live_at__isnull=True) | models.Q(go_live_at__lte=now),
            # If expire_at is set, now must be < expire_at
            models.Q(expire_at__isnull=True) | models.Q(expire_at__gt=now),
            page_types__page_type=page_content_type,
            segments__segment__in=segments,
        ).distinct()


class BasePersonalisedCallToAction(ClusterableModel):
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

    objects = models.Manager.from_queryset(PersonalisedCTAQuerySet)()

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        errors = {}

        if self.go_live_at and self.expire_at and self.expire_at <= self.go_live_at:
            errors["expire_at"] = "Expiry date/time must be after go live date/time"

        if errors:
            raise ValidationError(errors)


class UserActionChoicesMixin(models.Model):
    USER_ACTION_CHOICES = [
        ("page_load", "On page load"),
        ("inactivity", "On inactivity after X seconds"),
        ("scroll", "On scroll after X% of the way down"),
        ("exit_intent", "On exit intent"),
    ]

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

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        errors = {}

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

        if errors:
            raise ValidationError(errors)


class LinkFieldsMixin(models.Model):
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

    class Meta:
        abstract = True

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

        if errors:
            raise ValidationError(errors)


class UserActionCTASegment(Orderable):
    """This links a personalised CTA to a segment"""

    segment = models.ForeignKey(
        Segment, related_name="user_action_ctas", on_delete=models.CASCADE
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


class UserActionCallToAction(
    StyledPreviewableMixin,
    LinkFieldsMixin,
    UserActionChoicesMixin,
    BasePersonalisedCallToAction,
):
    image = models.ForeignKey(
        "images.CustomImage",
        on_delete=models.CASCADE,
        related_name="+",
    )
    title = models.CharField(max_length=40)
    description = models.CharField(max_length=65)

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
                "When the CTA should appear/expire. At least one date must be set "
                "for the CTA to be active. Leave both blank to disable the CTA."
            ),
        ),
    ]

    def __str__(self):
        return self.title

    def get_template_data(self):
        """
        Returns the data structure expected by the CTA modal template.
        This can be used both in preview and in actual page context.
        """
        data = {
            "image": self.image,
            "title": self.title,
            "description": self.description,
            "href": self.external_link
            or (self.internal_link.url if self.internal_link else ""),
            "text": self.link_label
            or (self.internal_link.title if self.internal_link else ""),
            "cta_id": self.pk,
            "cta_trigger": self.user_action,
        }

        # Add delay for inactivity trigger
        if self.user_action == "inactivity" and self.inactivity_seconds:
            data["cta_delay"] = self.inactivity_seconds

        # Add scroll percentage for scroll trigger
        if self.user_action == "scroll" and self.scroll_percentage:
            data["cta_scroll"] = self.scroll_percentage

        return data

    def get_preview_template(self, request, mode_name):
        return "patterns/molecules/cta_modal/cta_modal.html"

    def get_preview_context(self, request, mode_name):
        context = super().get_preview_context(request, mode_name)
        context.update(
            {
                "value": self.get_template_data(),
                "classes": "is-open",
            }
        )
        return context


class EmbeddedFooterCTASegment(Orderable):
    """This links a personalised CTA to a segment"""

    segment = models.ForeignKey(
        Segment, related_name="embedded_footer_ctas", on_delete=models.CASCADE
    )
    call_to_action = ParentalKey(
        "personalisation.EmbeddedFooterCallToAction", related_name="segments"
    )

    class Meta:
        unique_together = ("segment", "call_to_action")

    panels = [
        FieldPanel("segment"),
    ]


class EmbeddedFooterCTAPageType(Orderable):
    """
    This links a CTA to a page type so we know which page types to apply the CTA to.
    """

    page_type = models.CharField(
        max_length=100,
        choices=PAGE_TYPE_CHOICES,
        help_text="Select the page type where this CTA should appear",
    )
    call_to_action = ParentalKey(
        "personalisation.EmbeddedFooterCallToAction", related_name="page_types"
    )

    class Meta:
        unique_together = ("page_type", "call_to_action")

    panels = [
        FieldPanel("page_type"),
    ]

    def __str__(self):
        return self.get_page_type_display()


class EmbeddedFooterCallToAction(
    StyledPreviewableMixin, LinkFieldsMixin, BasePersonalisedCallToAction
):
    title = models.CharField(max_length=40)
    description = models.CharField(max_length=65)

    panels = [
        MultiFieldPanel(
            [
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
                "When the CTA should appear/expire. At least one date must "
                "be set for the CTA to be active. Leave both blank to disable the CTA."
            ),
        ),
    ]

    def __str__(self):
        return self.title

    def get_template_data(self):
        """
        Returns the data structure expected by the text-teaser template.
        This can be used both in preview and in actual page context.
        """
        teaser_data = {
            "title": self.title,
            "description": self.description,
        }

        if self.external_link:
            teaser_data["link"] = {"url": self.external_link}
            teaser_data["action"] = self.link_label
        elif self.internal_link:
            teaser_data["page"] = self.internal_link
            teaser_data["action"] = self.link_label or self.internal_link.title

        return teaser_data

    def get_preview_template(self, request, mode_name):
        return "patterns/molecules/text-teaser/text-teaser.html"

    def get_preview_context(self, request, mode_name):
        context = super().get_preview_context(request, mode_name)
        context["classes"] = "text-teaser--footer-cta"
        context["teaser"] = self.get_template_data()

        return context


class EventCountdownCTASegment(Orderable):
    segment = models.ForeignKey(
        Segment, related_name="event_countdown_ctas", on_delete=models.CASCADE
    )
    call_to_action = ParentalKey(
        "personalisation.EventCountdownCallToAction", related_name="segments"
    )

    class Meta:
        unique_together = ("segment", "call_to_action")

    panels = [
        FieldPanel("segment"),
    ]


class EventCountdownCTAPageType(Orderable):
    """
    This links a CTA to a page type so we know which page types to apply the CTA to.
    """

    page_type = models.CharField(
        max_length=100,
        choices=PAGE_TYPE_CHOICES,
        help_text="Select the page type where this CTA should appear",
    )
    call_to_action = ParentalKey(
        "personalisation.EventCountdownCallToAction", related_name="page_types"
    )

    class Meta:
        unique_together = ("page_type", "call_to_action")

    panels = [
        FieldPanel("page_type"),
    ]

    def __str__(self):
        return self.get_page_type_display()


class EventCountdownCallToAction(
    StyledPreviewableMixin,
    UserActionChoicesMixin,
    LinkFieldsMixin,
    BasePersonalisedCallToAction,
):
    title = models.CharField(max_length=40)

    # Date fields
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    countdown_timer_pre_text = models.CharField(blank=True)
    COUNTDOWN_TO_CHOICES = [
        ("start", "Start date"),
        ("end", "End date"),
    ]
    countdown_to = models.CharField(
        max_length=10,
        blank=True,
        choices=COUNTDOWN_TO_CHOICES,
        help_text="Choose which date the countdown must count to",
    )

    class Meta:
        verbose_name = "Event Countdown CTA"
        verbose_name_plural = "Event Countdown CTAs"

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                MultiFieldPanel(
                    [
                        PageChooserPanel("internal_link"),
                        FieldPanel("external_link"),
                        FieldPanel("link_label"),
                    ],
                    heading="Link (choose either internal or external)",
                ),
                MultiFieldPanel(
                    [
                        FieldPanel("start_date"),
                        FieldPanel("end_date"),
                        FieldPanel("countdown_to"),
                        FieldPanel("countdown_timer_pre_text"),
                    ],
                    heading="Countdown",
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
                "When the CTA should appear/expire. At least one date must "
                "be set for the CTA to be active. Leave both blank to disable the CTA."
            ),
        ),
    ]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        errors = {}

        # Validate countdown configuration
        if self.countdown_to:
            # If countdown_to is set, require the countdown_timer_pre_text
            if not self.countdown_timer_pre_text:
                errors["countdown_timer_pre_text"] = (
                    "Please provide the text that prepends the countdown timer"
                )

            # If counting down to start date, require start_date
            if self.countdown_to == "start" and not self.start_date:
                errors["start_date"] = (
                    "Please provide the start date for the countdown timer"
                )

            # If counting down to end date, require end_date
            if self.countdown_to == "end" and not self.end_date:
                errors["end_date"] = (
                    "Please provide the end date for the countdown timer"
                )

        # Validate that end_date is after start_date if both are provided
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            errors["end_date"] = "End date must be after start date"

        # Validate that dates are in the future
        now = timezone.now()
        if self.start_date and self.start_date < now:
            errors["start_date"] = "Start date cannot be in the past"

        if self.end_date and self.end_date < now:
            errors["end_date"] = "End date cannot be in the past"

        if errors:
            raise ValidationError(errors)

    def get_template_data(self):
        """
        Returns the data structure expected by the countdown CTA template.
        This can be used both in preview and in actual page context.
        """
        countdown_date = None
        if self.countdown_to == "end":
            countdown_date = self.end_date
        elif self.countdown_to == "start":
            countdown_date = self.start_date

        data = {
            "title": self.title,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "countdown_to": self.countdown_to,
            "countdown_text": self.countdown_timer_pre_text,
            "countdown_date": countdown_date,
            "link": {
                "link": self.external_link
                or (self.internal_link.url if self.internal_link else ""),
                "action": self.link_label
                or (self.internal_link.title if self.internal_link else ""),
            },
            "cta_id": self.pk,
            "cta_trigger": self.user_action,
        }

        # Add delay for inactivity trigger
        if self.user_action == "inactivity" and self.inactivity_seconds:
            data["cta_delay"] = self.inactivity_seconds

        # Add scroll percentage for scroll trigger
        if self.user_action == "scroll" and self.scroll_percentage:
            data["cta_scroll"] = self.scroll_percentage

        return data

    def get_preview_template(self, request, mode_name):
        return "patterns/organisms/countdown_cta/countdown_cta.html"

    def get_preview_context(self, request, mode_name):
        context = super().get_preview_context(request, mode_name)
        context["value"] = self.get_template_data()
        return context


class CollapsibleNavigationCTASegment(Orderable):
    """This links a personalised CTA to a segment"""

    segment = models.ForeignKey(
        Segment, related_name="collapsible_navigation_ctas", on_delete=models.CASCADE
    )
    call_to_action = ParentalKey(
        "personalisation.CollapsibleNavigationCallToAction", related_name="segments"
    )

    class Meta:
        unique_together = ("segment", "call_to_action")

    panels = [
        FieldPanel("segment"),
    ]


class CollapsibleNavigationCTAPageType(Orderable):
    """
    This links a CTA to a page type so we know which page types to apply the CTA to.
    """

    page_type = models.CharField(
        max_length=100,
        choices=PAGE_TYPE_CHOICES,
        help_text="Select the page type where this CTA should appear",
    )
    call_to_action = ParentalKey(
        "personalisation.CollapsibleNavigationCallToAction", related_name="page_types"
    )

    class Meta:
        unique_together = ("page_type", "call_to_action")

    panels = [
        FieldPanel("page_type"),
    ]

    def __str__(self):
        return self.get_page_type_display()


class CollapsibleNavigationCallToAction(
    StyledPreviewableMixin, BasePersonalisedCallToAction
):
    title = models.CharField(
        max_length=255, help_text="This is for internal purposes only."
    )
    links = StreamField(
        [
            ("link", CollapsibleNavigationLinkBlock()),
        ],
        max_num=5,
        min_num=2,
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("links"),
            ],
            heading="Content",
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
                "When the CTA should appear/expire. At least one date must "
                "be set for the CTA to be active. Leave both blank to disable the CTA."
            ),
        ),
    ]

    def __str__(self):
        return self.title

    def get_template_data(self):
        """
        Returns the data structure expected by the collapsible nav template.
        This can be used both in preview and in actual page context.
        """
        return [
            {
                "url": link.value["page"].url,
                "text": link.value["title"] or link.value["page"].title,
            }
            for link in self.links
        ]

    def get_preview_template(self, request, mode_name):
        return "patterns/molecules/collapsible_nav/collapsible_nav.html"

    def get_preview_context(self, request, mode_name):
        context = super().get_preview_context(request, mode_name)
        context["collapsible_nav"] = self.get_template_data()
        return context
