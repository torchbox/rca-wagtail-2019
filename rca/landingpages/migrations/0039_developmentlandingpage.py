# Generated by Django 3.1.10 on 2021-08-19 05:05

import django.db.models.deletion
import phonenumber_field.modelfields
import wagtail.core.blocks
import wagtail.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0003_extends_image_fields"),
        (
            "landingpages",
            "0038_adds_heading_and_swaps_external_links_for_additional_links",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="DevelopmentLandingPage",
            fields=[
                (
                    "landingpage_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="landingpages.landingpage",
                    ),
                ),
                ("location", wagtail.core.fields.RichTextField(blank=True)),
                (
                    "contact_tel",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, region=None
                    ),
                ),
                (
                    "contact_tel_display_text",
                    models.CharField(
                        blank=True,
                        help_text="Specify specific text or numbers to display for the linked tel number, e.g. +44 (0)20 7590 1234 or +44 (0)7749 183783",
                        max_length=120,
                    ),
                ),
                ("contact_email", models.EmailField(blank=True, max_length=254)),
                (
                    "social_links",
                    wagtail.core.fields.StreamField(
                        [
                            (
                                "Link",
                                wagtail.core.blocks.StructBlock(
                                    [
                                        (
                                            "title",
                                            wagtail.core.blocks.CharBlock(
                                                required=False
                                            ),
                                        ),
                                        (
                                            "url",
                                            wagtail.core.blocks.URLBlock(
                                                required=False
                                            ),
                                        ),
                                    ]
                                ),
                            )
                        ],
                        blank=True,
                    ),
                ),
                (
                    "video_caption",
                    models.CharField(
                        blank=True,
                        help_text="The text displayed next to the video play button",
                        max_length=80,
                    ),
                ),
                ("video", models.URLField(blank=True)),
                ("body", wagtail.core.fields.RichTextField(blank=True)),
                (
                    "video_preview_image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="images.customimage",
                    ),
                ),
            ],
            options={"abstract": False,},
            bases=("landingpages.landingpage",),
        ),
    ]
