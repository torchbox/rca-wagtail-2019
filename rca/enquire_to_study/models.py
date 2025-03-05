from django.db import models
from django_countries.fields import CountryField
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from phonenumber_field.modelfields import PhoneNumberField
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    HelpPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField
from wagtail.models import Orderable
from wagtail.snippets.models import register_snippet


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
    qs_code = models.CharField(
        max_length=500,
        help_text="This value needs to match the value of 'code' in the QS Intake item, E.G jan-18",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Enquiry form start date"
        verbose_name_plural = "Enquiry form start dates"

    def __str__(self):
        return self.label


class EnquiryFormSubmission(ClusterableModel):
    submission_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = PhoneNumberField()
    country_of_residence = CountryField()
    city = models.CharField(max_length=255)
    country_of_citizenship = CountryField()
    enquiry_reason = models.ForeignKey(
        "enquire_to_study.EnquiryReason",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    enquiry_questions = models.TextField(
        help_text="If you have a specific enquiry or question, please include it here.",
        max_length=1000,
        blank=True,
        null=True,
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
                FieldPanel("country_of_citizenship"),
            ],
            heading="Country of residence & citizenship",
        ),
        MultiFieldPanel(
            [InlinePanel("enquiry_submission_programmes")], heading="Programmes"
        ),
        FieldPanel("start_date"),
        FieldPanel("enquiry_reason", heading="What's your enquiry about?"),
        FieldPanel("enquiry_questions", heading="Your questions"),
        MultiFieldPanel(
            [
                FieldPanel("is_read_data_protection_policy"),
                FieldPanel("is_notification_opt_in"),
            ],
            heading="Legal & newsletter",
        ),
    ]


class EnquiryFormSubmissionProgrammesOrderable(Orderable):
    enquiry_submission = ParentalKey(
        "enquire_to_study.EnquiryFormSubmission",
        related_name="enquiry_submission_programmes",
    )
    programme = models.ForeignKey(
        "programmes.ProgrammePage",
        on_delete=models.CASCADE,
    )

    panels = [
        FieldPanel("programme"),
    ]


@register_setting
class EnquireToStudySettings(BaseSiteSetting):
    class Meta:
        verbose_name = "Register your interest settings"

    intro_heading = models.CharField(
        max_length=120,
        default="Register your interest",
    )
    intro_text = RichTextField(
        features=["bold", "italic", "link"],
        default=(
            "<p>We are very much looking forward to hearing more from you. "
            "The RCA offers a unique and life changing way of thinking about "
            "and approaching art and design study and practice. If you would "
            "like to find out more about studying at the RCA, please fill out "
            "your details below and we will be in touch. Fields marked * are "
            "required.</p>"
        ),
    )
    thank_you_heading = models.CharField(
        max_length=120,
        default=(
            "Thank you for your enquiry. We're excited that you're thinking of "
            "joining us."
        ),
    )
    thank_you_text = RichTextField(
        features=["bold", "italic", "link"],
        default=(
            "<p>Your enquiry has been passed to the relevant team and we'll be "
            "in touch soon with more information about your programme(s) of "
            "interest.</p>"
        ),
    )
    email_submission_notifations = models.BooleanField(
        default=True,
        help_text=(
            "When checked, submission confirmation email notifications will "
            "be sent to the user who filled out the form"
        ),
    )
    email_subject = models.CharField(max_length=255)
    email_content = models.TextField()

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("intro_heading"),
                FieldPanel("intro_text"),
                FieldPanel("thank_you_heading"),
                FieldPanel("thank_you_text"),
            ],
            "Content settings",
        ),
        MultiFieldPanel(
            [
                HelpPanel(
                    content=(
                        "Use the following fields to specify the contents of the "
                        "submission notification users will receive after submitting "
                        "the register your interest form"
                    )
                ),
                FieldPanel("email_submission_notifations"),
                FieldPanel("email_subject"),
                FieldPanel("email_content"),
            ],
            "Email notification settings",
        ),
    ]


@register_setting
class EnquiryFormKeyDetails(BaseSiteSetting):
    content = RichTextField(
        features=["h3", "bold", "italic", "link"],
    )

    panels = [FieldPanel("content")]
