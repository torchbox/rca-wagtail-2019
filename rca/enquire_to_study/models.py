from django.db import models
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from wagtail.admin.edit_handlers import MultiFieldPanel, FieldRowPanel, FieldPanel


class Submission(models.Model):
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
        ], help_text='User details'),

        MultiFieldPanel([
            FieldPanel('country_of_residence'),
            FieldPanel('city'),
            FieldPanel('is_citizen')
        ], help_text='Country of residence & citizenship'),

        FieldPanel('inquiry_reason', help_text="What's your enquiry about?"),
        FieldPanel('start_date'),

        MultiFieldPanel([
            FieldPanel('is_read_data_protection_policy'),
            FieldPanel('is_notification_opt_in'),
        ], help_text="Legal & newsletter"),
    ]


class Programme(models.Model):
    programme = models.CharField(max_length=255)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)


class Course(models.Model):
    course = models.CharField(max_length=255)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)


class Funding(models.Model):
    funding = models.CharField(max_length=255)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
