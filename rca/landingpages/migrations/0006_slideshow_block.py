# Generated by Django 2.2.12 on 2020-04-28 22:52

import django.db.models.deletion
import modelcluster.fields
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("landingpages", "0005_innovation_landing_page_fields")]

    operations = [
        migrations.CreateModel(
            name="HomePageSlideshowBlock",
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
                ("title", models.CharField(max_length=125)),
                ("summary", models.CharField(max_length=250)),
                (
                    "slides",
                    wagtail.fields.StreamField(
                        [
                            (
                                "slide",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "image",
                                            wagtail.images.blocks.ImageChooserBlock(),
                                        ),
                                        (
                                            "title",
                                            wagtail.blocks.CharBlock(
                                                required=False
                                            ),
                                        ),
                                        (
                                            "type",
                                            wagtail.blocks.CharBlock(
                                                required=False
                                            ),
                                        ),
                                        (
                                            "summary",
                                            wagtail.blocks.TextBlock(
                                                required=False
                                            ),
                                        ),
                                        (
                                            "link",
                                            wagtail.blocks.URLBlock(
                                                required=False
                                            ),
                                        ),
                                    ]
                                ),
                            )
                        ]
                    ),
                ),
                (
                    "source_page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="slideshow_block",
                        to="landingpages.LandingPage",
                    ),
                ),
            ],
        )
    ]
