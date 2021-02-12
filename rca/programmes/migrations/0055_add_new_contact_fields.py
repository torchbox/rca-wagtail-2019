# Generated by Django 2.2.12 on 2021-01-05 23:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0003_extends_image_fields"),
        ("forms", "0002_formfield_clean_name"),
        ("programmes", "0054_adds_staff_page_relationship"),
    ]
    run_before = [
        ("utils", "0019_update_contact_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="programmeindexpage",
            name="contact_model_email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="programmeindexpage",
            name="contact_model_form",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="forms.FormPage",
            ),
        ),
        migrations.AddField(
            model_name="programmeindexpage",
            name="contact_model_image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.CustomImage",
            ),
        ),
        migrations.AddField(
            model_name="programmeindexpage",
            name="contact_model_text",
            field=models.CharField(
                blank=True, help_text="Maximum length of 250 characters", max_length=250
            ),
        ),
        migrations.AddField(
            model_name="programmeindexpage",
            name="contact_model_title",
            field=models.CharField(
                blank=True, help_text="Maximum length of 120 characters", max_length=120
            ),
        ),
        migrations.AddField(
            model_name="programmeindexpage",
            name="contact_model_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="contact_model_email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="contact_model_form",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="forms.FormPage",
            ),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="contact_model_image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.CustomImage",
            ),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="contact_model_text",
            field=models.CharField(
                blank=True, help_text="Maximum length of 250 characters", max_length=250
            ),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="contact_model_title",
            field=models.CharField(
                blank=True, help_text="Maximum length of 120 characters", max_length=120
            ),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="contact_model_url",
            field=models.URLField(blank=True),
        ),
    ]
