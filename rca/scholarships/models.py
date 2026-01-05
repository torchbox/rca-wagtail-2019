from django import forms
from django.db import models
from django.shortcuts import reverse
from django.utils.http import urlencode
from django.utils.text import slugify
from django.utils.translation import gettext as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.snippets.models import register_snippet

from rca.programmes.models import ProgrammePage
from rca.utils.blocks import CallToActionBlock, StepBlock
from rca.utils.filter import TabStyleFilter
from rca.utils.models import BasePage, ContactFieldsMixin, SluggedTaxonomy

from .blocks import ScholarshipsListingPageBlock
from .filters import ProgrammeTabStyleFilter


class ScholarshipFeeStatus(SluggedTaxonomy):
    panels = [
        FieldPanel("title"),
    ]

    class Meta:
        ordering = ("title",)
        verbose_name_plural = "Scholarship Fee Statuses"


class ScholarshipFunding(SluggedTaxonomy):
    panels = [
        FieldPanel("title"),
    ]

    class Meta:
        ordering = ("title",)


class ScholarshipLocation(SluggedTaxonomy):
    panels = [
        FieldPanel("title"),
    ]

    class Meta:
        ordering = ("title",)


class ScholarshipEligibilityCriteria(SluggedTaxonomy):
    panels = [
        FieldPanel("title"),
    ]

    class Meta:
        ordering = ("title",)


@register_snippet
class Scholarship(models.Model):
    title = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    summary = models.CharField(max_length=255, blank=True)
    value = models.CharField(max_length=100)
    location = models.ForeignKey(
        ScholarshipLocation, null=True, on_delete=models.SET_NULL
    )
    eligable_programmes = models.ManyToManyField(ProgrammePage)
    other_criteria = models.ManyToManyField(ScholarshipFunding)
    fee_statuses = models.ManyToManyField(ScholarshipFeeStatus)

    class Meta:
        ordering = ("title",)

    def __str__(self) -> str:
        text = self.title
        if self.location:
            text += f" ({self.location})"
        return text


class ScholarshipsListingPage(ContactFieldsMixin, BasePage):
    template = "patterns/pages/scholarships/scholarships_listing_page.html"
    max_count = 1
    introduction = models.CharField(max_length=500, blank=True)
    body = StreamField(ScholarshipsListingPageBlock())

    class BackgroundColor(models.TextChoices):
        LIGHT = "light", "Light"
        DARK = "dark", "Dark"

    # Scholarship listing fields
    scholarships_listing_background_color = models.CharField(
        max_length=10,
        choices=BackgroundColor.choices,
        default="light",
        help_text="Select the background color for this section",
        verbose_name="Background Color",
    )
    scholarship_listing_title = models.CharField(
        max_length=50, verbose_name="Listing Title"
    )
    scholarship_listing_sub_title = models.CharField(
        blank=True, max_length=100, verbose_name="Listing Subtitle"
    )
    scholarship_application_steps = StreamField(
        [
            ("step", StepBlock()),
            ("step_snippet", SnippetChooserBlock("utils.StepSnippet")),
        ],
        blank=True,
        verbose_name="Application Steps",
    )
    characteristics_disclaimer = models.CharField(
        max_length=250,
        blank=True,
        help_text="A small disclaimer shown just above the scholarships listing.",
    )

    # Scholarship form fields
    key_details = RichTextField(features=["h3", "bold", "italic", "link"], blank=True)
    form_introduction = models.CharField(max_length=500, blank=True)
    cta_block = StreamField(
        [("call_to_action", CallToActionBlock(label="text promo"))],
        blank=True,
        verbose_name="Call to action",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        MultiFieldPanel(
            [
                FieldPanel("scholarships_listing_background_color"),
                FieldPanel("scholarship_listing_title"),
                FieldPanel("scholarship_listing_sub_title"),
                FieldPanel("scholarship_application_steps"),
                FieldPanel("characteristics_disclaimer"),
            ],
            heading="Scholarship listing",
        ),
        FieldPanel("body"),
        MultiFieldPanel([*ContactFieldsMixin.panels], heading="Contact information"),
    ]

    form_settings_pannels = [
        FieldPanel("key_details"),
        FieldPanel("form_introduction"),
        FieldPanel("cta_block"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
            ObjectList(form_settings_pannels, heading="Enquiry form settings"),
        ]
    )

    @property
    def show_interest_bar(self):
        return True

    @property
    def show_interest_link(self):
        return True

    @property
    def scholarships_has_dark_background(self):
        return self.scholarships_listing_background_color == self.BackgroundColor.DARK

    def anchor_nav(self):
        """Build list of data to be used as in-page navigation"""
        items = []

        def process_block(block):
            if block.block_type == "anchor_heading":
                items.append({"title": block.value, "link": f"#{slugify(block.value)}"})

        for block in self.body:
            process_block(block)

        # insert link for hardcoded "Scholarships for YYYY/YY" heading
        items.append(
            {
                "title": self.scholarship_listing_title,
                "link": "#scholarship-listing-title",
            }
        )

        return items

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        programme = None
        results = []
        queryset = Scholarship.objects.filter(active=True).prefetch_related(
            "eligable_programmes", "other_criteria", "fee_statuses"
        )

        filters = (
            ProgrammeTabStyleFilter(
                "Programme",
                queryset=(
                    ProgrammePage.objects.filter(
                        id__in=queryset.values_list(
                            "eligable_programmes__id", flat=True
                        )
                    ).live()
                ),
                filter_by="eligable_programmes__slug__in",
                option_value_field="slug",
            ),
            TabStyleFilter(
                "Fee Status",
                queryset=(
                    ScholarshipLocation.objects.filter(
                        id__in=queryset.values_list("location_id", flat=True)
                    )
                ),
                filter_by="location__slug__in",
                option_value_field="slug",
            ),
        )

        if "programme" in request.GET or "location" in request.GET:
            # Apply filters
            for f in filters:
                queryset = f.apply(queryset, request.GET)

            # Format scholarships for template
            results = [
                {
                    "value": {
                        "heading": s.title,
                        "introduction": s.summary,
                        "eligible_programmes": ", ".join(
                            str(x) for x in s.eligable_programmes.live()
                        ),
                        "other_criteria": ", ".join(
                            x.title for x in s.other_criteria.all()
                        ),
                        "fee_statuses": ", ".join(
                            x.title for x in s.fee_statuses.all()
                        ),
                        "value": s.value,
                    }
                }
                for s in queryset
            ]

            # Template needs the programme for title and slug
            try:
                programme = ProgrammePage.objects.get(slug=request.GET["programme"])
            except Exception:
                pass

        # Create the link for the sticky CTA
        interest_bar_link = reverse("scholarships:scholarship_enquiry_form")
        if programme:
            interest_bar_link += f"?{urlencode({'programme': programme.slug})}"

        context.update(
            anchor_nav=self.anchor_nav(),
            filters={
                "title": _("Filter by"),
                "aria_label": "Filter results",
                "items": filters,
            },
            interest_bar={
                "action": _("Express interest"),
                "link": interest_bar_link,
                "message": _("Hold an offer and want to apply for these scholarships?"),
                "link_same_page": True,
            },
            programme=programme,
            results=results,
        )
        return context


class ScholarshipEnquiryFormSubmissionScholarshipOrderable(Orderable):
    scholarship_submission = ParentalKey(
        "scholarships.ScholarshipEnquiryFormSubmission",
        related_name="scholarship_submission_scholarships",
    )
    scholarship = models.ForeignKey(
        "scholarships.Scholarship",
        on_delete=models.CASCADE,
    )

    panels = [
        FieldPanel("scholarship"),
    ]


class ScholarshipEnquiryFormSubmission(ClusterableModel):
    submission_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    rca_id_number = models.CharField(max_length=100)
    programme = models.ForeignKey(
        "programmes.ProgrammePage",
        on_delete=models.CASCADE,
    )
    eligibility_criteria = models.ManyToManyField(
        ScholarshipEligibilityCriteria, blank=True
    )
    is_read_data_protection_policy = models.BooleanField()
    is_notification_opt_in = models.BooleanField()

    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("first_name", classname="fn"),
                        FieldPanel("last_name", classname="ln"),
                    ]
                ),
                FieldPanel("rca_id_number"),
            ],
            heading="User details",
        ),
        FieldPanel("programme"),
        InlinePanel("scholarship_submission_scholarships", label="Scholarship"),
        FieldPanel("eligibility_criteria", widget=forms.CheckboxSelectMultiple),
        MultiFieldPanel(
            [
                FieldPanel("is_read_data_protection_policy"),
                FieldPanel("is_notification_opt_in"),
            ],
            heading="Legal & newsletter",
        ),
    ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.rca_id_number}"

    def get_scholarships(self):
        return [s.scholarship for s in self.scholarship_submission_scholarships.all()]
