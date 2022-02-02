# Generated by Django 3.2.11 on 2022-02-01 14:22

import wagtail.core.blocks
import wagtail.core.fields
import wagtail.embeds.blocks
import wagtail.images.blocks
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0013_convert_event_date_to_date_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eventdetailpage",
            name="body",
            field=wagtail.core.fields.StreamField(
                [
                    ("image", wagtail.images.blocks.ImageChooserBlock()),
                    (
                        "heading",
                        wagtail.core.blocks.CharBlock(
                            form_classname="full title",
                            icon="title",
                            template="patterns/molecules/streamfield/blocks/heading_block.html",
                        ),
                    ),
                    ("paragraph", wagtail.core.blocks.RichTextBlock()),
                    (
                        "quote",
                        wagtail.core.blocks.StructBlock(
                            [
                                (
                                    "quote",
                                    wagtail.core.blocks.CharBlock(
                                        form_classname="title",
                                        help_text="Enter quote text only, there is no need to add quotation marks",
                                    ),
                                ),
                                (
                                    "author",
                                    wagtail.core.blocks.CharBlock(required=False),
                                ),
                                (
                                    "job_title",
                                    wagtail.core.blocks.CharBlock(required=False),
                                ),
                            ]
                        ),
                    ),
                    ("embed", wagtail.embeds.blocks.EmbedBlock()),
                    (
                        "jw_video",
                        wagtail.core.blocks.StructBlock(
                            [
                                (
                                    "title",
                                    wagtail.core.blocks.CharBlock(
                                        help_text="Optional title to identify the video. Not shown on the page.",
                                        required=False,
                                    ),
                                ),
                                (
                                    "video_url",
                                    wagtail.core.blocks.URLBlock(
                                        help_text="The URL of the video to show.",
                                        max_length=1000,
                                    ),
                                ),
                                (
                                    "poster_image",
                                    wagtail.images.blocks.ImageChooserBlock(
                                        help_text="The poster image to show as a placeholder for the video. For best results use an image 1920x1080 pixels"
                                    ),
                                ),
                            ]
                        ),
                    ),
                ]
            ),
        ),
    ]
