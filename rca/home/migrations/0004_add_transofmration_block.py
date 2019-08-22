# Generated by Django 2.2.4 on 2019-08-22 19:58

import django.db.models.deletion
import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0002_customimage_file_hash"),
        ("home", "0003_add_hero_and_cta_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomePageTransofmrationBlock",
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
                        help_text="Large heading displayed above the image",
                        max_length=125,
                    ),
                ),
                ("video", models.URLField(blank=True)),
                (
                    "video_caption",
                    models.CharField(
                        blank=True,
                        help_text="The text dipsplayed next to the video play button",
                        max_length=80,
                    ),
                ),
                (
                    "sub_heading",
                    models.CharField(
                        blank=True,
                        help_text="The title below the image",
                        max_length=125,
                    ),
                ),
                (
                    "page_title",
                    models.CharField(
                        blank=True,
                        help_text="A title for the linked related page",
                        max_length=125,
                    ),
                ),
                (
                    "page_summary",
                    models.CharField(
                        blank=True,
                        help_text="A summary for the linked related page",
                        max_length=250,
                    ),
                ),
                (
                    "page_link_url",
                    models.URLField(blank=True, help_text="A url to a related page"),
                ),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="images.CustomImage",
                    ),
                ),
                (
                    "source_page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transformation_blocks",
                        to="home.HomePage",
                    ),
                ),
            ],
        )
    ]
