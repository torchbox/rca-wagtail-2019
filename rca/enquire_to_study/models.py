from django.db import models
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


class InquiryReason(models.Model):
    reason = models.CharField(max_length=255)


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


class Programme(models.Model):
    programme = models.CharField(max_length=255)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)


class Course(models.Model):
    course = models.CharField(max_length=255)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)


class Funding(models.Model):
    funding = models.CharField(max_length=255)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
