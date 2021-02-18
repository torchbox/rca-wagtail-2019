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
        verbose_name='Enquirey form funding option'
        verbose_name_plural='Enquirey form funding options'
        
    def __str__(self):
        return self.funding


@register_snippet
class InquiryReason(models.Model):
    reason = models.CharField(max_length=255)
     
     class Meta:
        verbose_name='Enquirey form reason'
        verbose_name_plural='Enquirey form reasons'
        
    def __str__(self):
        return self.reason


@register_snippet
class StartDate(models.Model):
    label = models.CharField(max_length=255)
    start_date = models.DateField()

    def __str__(self):
        return self.label


class Submission(ClusterableModel):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = PhoneNumberField()
    country_of_residence = CountryField()
    city = models.CharField(max_length=255)
    is_citizen = models.BooleanField()
    inquiry_reason = models.ForeignKey(
        "enquire_to_study.InquiryReason",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    start_date = models.CharField(max_length=255)
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
        MultiFieldPanel([InlinePanel("submissions_programmes")], heading="Programmes"),
        MultiFieldPanel([InlinePanel("submissions_courses")], heading="Courses"),
        FieldPanel("start_date"),
        MultiFieldPanel([InlinePanel("submissions_funding")], heading="Funding"),
        SnippetChooserPanel("inquiry_reason", heading="What's your enquiry about?"),
        MultiFieldPanel(
            [
                FieldPanel("is_read_data_protection_policy"),
                FieldPanel("is_notification_opt_in"),
            ],
            heading="Legal & newsletter",
        ),
    ]


class SubmissionFundingsOrderable(Orderable):
    submission = ParentalKey(
        "enquire_to_study.Submission", related_name="submissions_funding"
    )
    funding = models.ForeignKey("enquire_to_study.Funding", on_delete=models.CASCADE,)

    panels = [
        SnippetChooserPanel("funding"),
    ]
