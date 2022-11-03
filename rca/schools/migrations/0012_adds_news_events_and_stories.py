# Generated by Django 2.2.12 on 2021-01-14 19:34

import django.db.models.deletion
import modelcluster.contrib.taggit
import modelcluster.fields
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("utils", "0018_name_updates"),
        ("schools", "0011_add_related_programmes_and_courses"),
    ]

    operations = [
        migrations.AddField(
            model_name="schoolpage",
            name="legacy_news_and_event_tags",
            field=modelcluster.contrib.taggit.ClusterTaggableManager(
                blank=True,
                help_text="Specify one or more tags to identify related news and events from the legacy site. A maximum of three items with the same combination of tags will then be displayed on the page.",
                through="utils.LegacySiteTaggedPage",
                to="utils.LegacySiteTag",
                verbose_name="Legacy news and events tags",
            ),
        ),
        migrations.AddField(
            model_name="schoolpage",
            name="news_and_events_heading",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.CreateModel(
            name="StudentPageStudentStories",
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
                (
                    "slides",
                    wagtail.fields.StreamField(
                        [
                            (
                                "Page",
                                wagtail.blocks.StreamBlock(
                                    [
                                        (
                                            "page",
                                            wagtail.blocks.PageChooserBlock(),
                                        ),
                                        (
                                            "custom_teaser",
                                            wagtail.blocks.StructBlock(
                                                [
                                                    (
                                                        "title",
                                                        wagtail.blocks.CharBlock(
                                                            required=False
                                                        ),
                                                    ),
                                                    (
                                                        "meta",
                                                        wagtail.blocks.CharBlock(
                                                            help_text="Small tag value displayed below the title",
                                                            required=False,
                                                        ),
                                                    ),
                                                    (
                                                        "text",
                                                        wagtail.blocks.CharBlock(
                                                            required=False
                                                        ),
                                                    ),
                                                    (
                                                        "image",
                                                        wagtail.images.blocks.ImageChooserBlock(),
                                                    ),
                                                    (
                                                        "link",
                                                        wagtail.blocks.StructBlock(
                                                            [
                                                                (
                                                                    "title",
                                                                    wagtail.blocks.CharBlock(
                                                                        required=False
                                                                    ),
                                                                ),
                                                                (
                                                                    "url",
                                                                    wagtail.blocks.URLBlock(
                                                                        required=False
                                                                    ),
                                                                ),
                                                            ],
                                                            required=False,
                                                        ),
                                                    ),
                                                ]
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
                        related_name="student_stories",
                        to="schools.SchoolPage",
                    ),
                ),
            ],
        ),
    ]
