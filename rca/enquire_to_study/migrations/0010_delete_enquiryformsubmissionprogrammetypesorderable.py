# Generated by Django 3.1.10 on 2021-08-10 09:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("enquire_to_study", "0009_add_smailchimp_label_to_startdate"),
    ]

    operations = [
        migrations.DeleteModel(name="EnquiryFormSubmissionProgrammeTypesOrderable",),
    ]
