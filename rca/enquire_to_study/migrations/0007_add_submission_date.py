# Generated by Django 2.2.12 on 2021-03-16 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("enquire_to_study", "0006_merge_20210312_1111"),
    ]

    operations = [
        migrations.AddField(
            model_name="enquiryformsubmission",
            name="submission_date",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
