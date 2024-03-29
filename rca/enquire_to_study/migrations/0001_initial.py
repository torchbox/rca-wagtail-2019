# Generated by Django 2.2.12 on 2021-02-18 07:00

import django.db.models.deletion
import django_countries.fields
import modelcluster.fields
import phonenumber_field.modelfields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Funding",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("funding", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="InquiryReason",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("reason", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="StartDate",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("label", models.CharField(max_length=255)),
                ("start_date", models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name="Submission",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254)),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        max_length=128, region=None
                    ),
                ),
                (
                    "country_of_residence",
                    django_countries.fields.CountryField(max_length=2),
                ),
                ("city", models.CharField(max_length=255)),
                ("is_citizen", models.BooleanField()),
                ("start_date", models.CharField(max_length=255)),
                ("is_read_data_protection_policy", models.BooleanField()),
                ("is_notification_opt_in", models.BooleanField()),
                (
                    "inquiry_reason",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="enquire_to_study.InquiryReason",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SubmissionFundingsOrderable",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                (
                    "funding",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="enquire_to_study.Funding",
                    ),
                ),
                (
                    "submission",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions_funding",
                        to="enquire_to_study.Submission",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
    ]
