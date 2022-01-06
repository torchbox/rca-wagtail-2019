from django.db import models
from django.utils.text import slugify
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    StreamFieldPanel,
    TabbedInterface,
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet

from rca.programmes.models import ProgrammePage
from rca.scholarships.blocks import ScholarshipsListingPageBlock
from rca.utils.blocks import CallToActionBlock
from rca.utils.models import BasePage, ContactFieldsMixin, SluggedTaxonomy


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


@register_snippet
class Scholarship(models.Model):
    title = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    summary = models.CharField(max_length=255)
    value = models.CharField(max_length=100)
    eligable_programmes = models.ManyToManyField(ProgrammePage)
    funding_categories = models.ManyToManyField(ScholarshipFunding)
    fee_statuses = models.ManyToManyField(ScholarshipFeeStatus)

    def __str__(self) -> str:
        return self.title


class ScholarshipsListingPage(ContactFieldsMixin, BasePage):
    template = "patterns/pages/scholarships/scholarships_listing_page.html"
    max_count = 1
    introduction = models.CharField(max_length=500, blank=True)
    body = StreamField(ScholarshipsListingPageBlock())
    characteristics_disclaimer = models.CharField(
        max_length=250,
        blank=True,
        help_text="A small disclaimer shown just above the scholarships listing.",
    )
    lower_body = StreamField(ScholarshipsListingPageBlock())

    key_details = RichTextField(features=["h3", "bold", "italic", "link"], blank=True)
    form_introduction = models.CharField(max_length=500, blank=True)
    cta_block = StreamField(
        [("call_to_action", CallToActionBlock(label="text promo"))],
        blank=True,
        verbose_name="Call to action",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("introduction"),
        StreamFieldPanel("body"),
        MultiFieldPanel(
            [FieldPanel("characteristics_disclaimer")], heading="Scholarship listing"
        ),
        StreamFieldPanel("lower_body"),
        MultiFieldPanel([*ContactFieldsMixin.panels], heading="Contact information"),
    ]

    form_settings_pannels = [
        FieldPanel("key_details"),
        FieldPanel("form_introduction"),
        StreamFieldPanel("cta_block"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(BasePage.promote_panels, heading="Promote"),
            ObjectList(BasePage.settings_panels, heading="Settings"),
            ObjectList(form_settings_pannels, heading="Enquiry form settings"),
        ]
    )

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
                "title": "Scholarships for 2022/23 entry",
                "link": "#scholarships-for-entry",
            }
        )

        for block in self.lower_body:
            process_block(block)

        return items

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["anchor_nav"] = self.anchor_nav()
        return context


class ScholarshipEnquiryFormSubmissionScholarshipOrderable(Orderable):
    scholarship_submission = ParentalKey(
        "scholarships.ScholarshipEnquiryFormSubmission",
        related_name="scholarship_submission_scholarships",
    )
    scholarship = models.ForeignKey(
        "scholarships.Scholarship", on_delete=models.CASCADE,
    )

    panels = [
        SnippetChooserPanel("scholarship"),
    ]


class ScholarshipEnquiryFormSubmission(ClusterableModel):
    submission_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    rca_id_number = models.CharField(max_length=100)
    programme = models.ForeignKey("programmes.ProgrammePage", on_delete=models.CASCADE,)

    # TODO
    # related Scholarship snippet
    # Scholarship eligibility (needs confirmation of choices from RCA) - these will be  hardcoded.

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
