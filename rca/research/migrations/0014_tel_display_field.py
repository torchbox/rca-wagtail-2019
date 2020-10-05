# Generated by Django 2.2.12 on 2020-10-05 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("research", "0013_merge_20200806_1444"),
    ]

    operations = [
        migrations.AddField(
            model_name="researchcentrepage",
            name="centre_tel_display_text",
            field=models.CharField(
                blank=True,
                help_text="Specify specific text or numbers to display for the linked tel number",
                max_length=120,
            ),
        ),
    ]
