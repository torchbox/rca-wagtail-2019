# Generated by Django 2.2.4 on 2019-09-06 09:53

import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("utils", "0004_replace_facilities_fields_with_snippet")]

    operations = [
        migrations.CreateModel(
            name="AccordionSnippet",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "heading",
                    models.CharField(
                        blank=True,
                        help_text="A large heading diplayed next to the block",
                        max_length=125,
                    ),
                ),
                (
                    "admin_title",
                    models.CharField(
                        help_text="The title value is only used to identify the snippet in the admin interface ",
                        max_length=255,
                    ),
                ),
                (
                    "preview_text",
                    models.CharField(
                        blank=True,
                        help_text="The text to display when the accordion is collapsed",
                        max_length=250,
                    ),
                ),
                (
                    "body",
                    wagtail.fields.RichTextField(
                        help_text="The content shown when the accordion expanded"
                    ),
                ),
                ("link_url", models.URLField(blank=True)),
                ("link_title", models.CharField(blank=True, max_length=125)),
            ],
        )
    ]
