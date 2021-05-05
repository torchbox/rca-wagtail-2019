# Generated by Django 2.2.12 on 2021-03-10 16:21

import django_countries.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("enquire_to_study", "0004_remove_funding"),
    ]

    operations = [
        migrations.RemoveField(model_name="enquiryformsubmission", name="is_citizen",),
        migrations.AddField(
            model_name="enquiryformsubmission",
            name="country_of_citizenship",
            field=django_countries.fields.CountryField(default="", max_length=2),
            preserve_default=False,
        ),
    ]