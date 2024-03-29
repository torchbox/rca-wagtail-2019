# Generated by Django 2.2.12 on 2021-01-05 16:36
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def update_form_fields(apps, schema_editor):
    models = [
        apps.get_model("guides", "GuidePage"),
        apps.get_model("landingpages", "LandingPage"),
        apps.get_model("programmes", "ProgrammePage"),
        apps.get_model("programmes", "ProgrammeIndexPage"),
        apps.get_model("projects", "ProjectPage"),
        apps.get_model("shortcourses", "ShortCoursePage"),
    ]

    for model in models:
        for page in model.objects.all():
            if hasattr(page, "contact_email"):
                page.contact_model_email = page.contact_email
            if hasattr(page, "contact_text"):
                page.contact_model_text = page.contact_text
            if hasattr(page, "contact_image"):
                page.contact_model_image = page.contact_image
            if hasattr(page, "contact_url"):
                page.contact_model_url = page.contact_url
            if hasattr(page, "contact_title"):
                page.contact_model_title = page.contact_title
            page.save()


class Migration(migrations.Migration):

    dependencies = [
        ("utils", "0018_name_updates"),
    ]

    operations = [
        migrations.RunPython(update_form_fields),
    ]
