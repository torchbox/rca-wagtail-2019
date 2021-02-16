from django.db import models
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


class Programme(models.Model):
    program = models.CharField(max_length=255)


class Course(models.Model):
    course = models.CharField(max_length=255)


class StartDate(models.Model):
    start_date = models.CharField(max_length=255)


class Funding(models.Model):
    funding = models.CharField(max_length=255)


class InquiryReason(models.Model):
    funding = models.CharField(max_length=255)


class Submission(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = PhoneNumberField()
    country_of_residence = CountryField()
    city = models.CharField(max_length=255)
    is_citizen = models.CharField(max_length=255)
    programmes = models.ForeignKey(Programme, on_delete=models.CASCADE)
    courses = models.ForeignKey(Programme, on_delete=models.CASCADE)
    start_date = models.OneToOneField(
        StartDate,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    funding = models.ForeignKey(Funding, on_delete=models.CASCADE)
    inquiry_reason = models.ForeignKey(InquiryReason, on_delete=models.CASCADE)
    is_read_data_protection_policy = models.BooleanField()
    is_notification_opt_in = models.BooleanField()
