from django.db import models
from django_countries.fields import CountryField
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from phonenumber_field.modelfields import PhoneNumberField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.core.models import Orderable
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class Funding(models.Model):
    funding = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Enquiry form funding option"
        verbose_name_plural = "Enquiry form funding options"

    def __str__(self):
        return self.funding


@register_snippet
class EnquiryReason(models.Model):
    reason = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Enquiry form reason"
        verbose_name_plural = "Enquiry form reasons"

    def __str__(self):
        return self.reason


@register_snippet
class StartDate(models.Model):
    label = models.CharField(max_length=255)
    start_date = models.DateField()

    class Meta:
        verbose_name = "Enquiry form start date"
        verbose_name_plural = "Enquiry form start dates"

    def __str__(self):
        return self.label


class EnquiryFormSubmission(ClusterableModel):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = PhoneNumberField()
    country_of_residence = CountryField()
    city = models.CharField(max_length=255)
    is_citizen = models.BooleanField()
    enquiry_reason = models.ForeignKey(
        "enquire_to_study.EnquiryReason",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    start_date = models.ForeignKey(
        "enquire_to_study.StartDate",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
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
                FieldPanel("email"),
                FieldPanel("phone_number"),
            ],
            heading="User details",
        ),
        MultiFieldPanel(
            [
                FieldPanel("country_of_residence"),
                FieldPanel("city"),
                FieldPanel("is_citizen"),
            ],
            heading="Country of residence & citizenship",
        ),
        MultiFieldPanel(
            [InlinePanel("enquiry_submission_programme_types")],
            heading="Programmes Types",
        ),
        MultiFieldPanel(
            [InlinePanel("enquiry_submission_programmes")], heading="Programmes"
        ),
        FieldPanel("start_date"),
        MultiFieldPanel([InlinePanel("enquiry_submission_funding")], heading="Funding"),
        SnippetChooserPanel("enquiry_reason", heading="What's your enquiry about?"),
        MultiFieldPanel(
            [
                FieldPanel("is_read_data_protection_policy"),
                FieldPanel("is_notification_opt_in"),
            ],
            heading="Legal & newsletter",
        ),
    ]


class EnquiryFormSubmissionFundingsOrderable(Orderable):
    enquiry_submission = ParentalKey(
        "enquire_to_study.EnquiryFormSubmission",
        related_name="enquiry_submission_funding",
    )
    funding = models.ForeignKey("enquire_to_study.Funding", on_delete=models.CASCADE,)

    panels = [
        SnippetChooserPanel("funding"),
    ]


class EnquiryFormSubmissionProgrammeTypesOrderable(Orderable):
    enquiry_submission = ParentalKey(
        "enquire_to_study.EnquiryFormSubmission",
        related_name="enquiry_submission_programme_types",
    )
    programme_type = models.ForeignKey(
        "programmes.ProgrammeType", on_delete=models.CASCADE,
    )

    panels = [
        SnippetChooserPanel("programme_type"),
    ]


class EnquiryFormSubmissionProgrammesOrderable(Orderable):
    enquiry_submission = ParentalKey(
        "enquire_to_study.EnquiryFormSubmission",
        related_name="enquiry_submission_programmes",
    )
    programme = models.ForeignKey("programmes.ProgrammePage", on_delete=models.CASCADE,)

    panels = [
        SnippetChooserPanel("programme"),
    ]
