from django.db import models
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


class Submission(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = PhoneNumberField()
    country_of_residence = CountryField()
    city = models.CharField(max_length=255)
    is_citizen = models.CharField(max_length=255)
    programmes = models.CharField(max_length=255)
    courses = models.CharField(max_length=255)
    start_date = models.CharField(max_length=255)
    funding = models.CharField(max_length=255)
    inquiry_reason = models.CharField(max_length=255)
    is_read_data_protection_policy = models.BooleanField()
    is_notification_opt_in = models.BooleanField()
