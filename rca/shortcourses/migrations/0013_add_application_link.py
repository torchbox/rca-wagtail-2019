# Generated by Django 2.2.12 on 2020-05-01 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("shortcourses", "0012_add_teaser_help_text")]

    operations = [
        migrations.AddField(
            model_name="shortcoursepage",
            name="application_form_url",
            field=models.URLField(blank=True),
        )
    ]
