# Generated by Django 2.2.12 on 2020-04-22 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("research", "0002_field_additions_and_related_models")]

    operations = [
        migrations.AddField(
            model_name="researchcentrepage",
            name="staff_link",
            field=models.URLField(blank=True, help_text="Add a link to see all staff"),
        ),
        migrations.AddField(
            model_name="researchcentrepage",
            name="staff_link_text",
            field=models.CharField(
                blank=True,
                help_text="The text to display on the link to all staff",
                max_length=80,
            ),
        ),
    ]
