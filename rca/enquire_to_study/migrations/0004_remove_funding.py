# Generated by Django 2.2.12 on 2021-03-09 12:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("enquire_to_study", "0003_enquiry_submission"),
    ]

    operations = [
        migrations.DeleteModel(
            name="EnquiryFormSubmissionFundingsOrderable",
        ),
        migrations.DeleteModel(
            name="Funding",
        ),
    ]
