from django.db import models
from django_countries.fields import CountryField
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from phonenumber_field.modelfields import PhoneNumberField
from wagtail.admin.edit_handlers import MultiFieldPanel, FieldRowPanel, FieldPanel, InlinePanel
from wagtail.core.models import Orderable
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class Programme(models.Model):
    programme = models.CharField(max_length=255)

    def __str__(self):
        return self.programme


@register_snippet
class Course(models.Model):
    course = models.CharField(max_length=255)

    def __str__(self):
        return self.course


@register_snippet
class Funding(models.Model):
    funding = models.CharField(max_length=255)

    def __str__(self):
        return self.funding


class Submission(ClusterableModel):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = PhoneNumberField()
    country_of_residence = CountryField()
    city = models.CharField(max_length=255)
    is_citizen = models.BooleanField()
    inquiry_reason = models.CharField(max_length=255)
    start_date = models.CharField(max_length=255)
    is_read_data_protection_policy = models.BooleanField()
    is_notification_opt_in = models.BooleanField()

    panels = [
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('first_name', classname='fn'),
                FieldPanel('last_name', classname='ln'),
            ]),
            FieldPanel('email'),
            FieldPanel('phone_number'),
        ], heading='User details'),

        MultiFieldPanel([
            FieldPanel('country_of_residence'),
            FieldPanel('city'),
            FieldPanel('is_citizen')
        ], heading='Country of residence & citizenship'),

        FieldPanel('inquiry_reason', help_text="What's your enquiry about?"),
        FieldPanel('start_date'),
        MultiFieldPanel(
            [
                InlinePanel("submissions_programmes")
            ],
            heading="Programmes"
        ),
        MultiFieldPanel(
            [
                InlinePanel("submissions_courses")
            ],
            heading="Courses"
        ),
        MultiFieldPanel(
            [
                InlinePanel("submissions_funding")
            ],
            heading="Funding"
        ),
        MultiFieldPanel([
            FieldPanel('is_read_data_protection_policy'),
            FieldPanel('is_notification_opt_in'),
        ], heading="Legal & newsletter"),
    ]


class SubmissionProgrammesOrderable(Orderable):
    submission = ParentalKey("enquire_to_study.Submission", related_name="submissions_programmes")
    programme = models.ForeignKey(
        "enquire_to_study.Programme",
        on_delete=models.CASCADE,
    )

    panels = [
        SnippetChooserPanel("programme"),
    ]


class SubmissionCoursesOrderable(Orderable):
    submission = ParentalKey("enquire_to_study.Submission", related_name="submissions_courses")
    course = models.ForeignKey(
        "enquire_to_study.Course",
        on_delete=models.CASCADE,
    )

    panels = [
        SnippetChooserPanel("course"),
    ]


class SubmissionFundingsOrderable(Orderable):
    submission = ParentalKey("enquire_to_study.Submission", related_name="submissions_funding")
    funding = models.ForeignKey(
        "enquire_to_study.Funding",
        on_delete=models.CASCADE,
    )

    panels = [
        SnippetChooserPanel("funding"),
    ]
