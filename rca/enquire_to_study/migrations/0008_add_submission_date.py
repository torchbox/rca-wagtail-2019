# Generated by Django 2.2.12 on 2021-03-16 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("enquire_to_study", "0007_merge_20210314_1919"),
    ]

    operations = [
        migrations.AddField(
            model_name="enquiryformsubmission",
            name="submission_date",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
