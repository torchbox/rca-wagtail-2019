# Generated by Django 2.2.4 on 2019-08-19 11:38

import django.db.models.deletion
import wagtail.blocks
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0002_customimage_file_hash"),
        ("programmes", "0003_remaining_overview_section_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="programmepage",
            name="curriculum_image",
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
            name="curriculum_subtitle",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="curriculum_text",
            field=models.TextField(blank=True, max_length=250),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="curriculum_video",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="curriculum_video_caption",
            field=models.CharField(
                blank=True,
                help_text="The text dipsplayed next to the video play button",
                max_length=80,
            ),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="pathway_blocks",
            field=wagtail.fields.StreamField(
                [
                    (
                        "accordion_block",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "heading",
                                    wagtail.blocks.CharBlock(
                                        help_text="A large heading diplayed next to the block",
                                        required=False,
                                    ),
                                ),
                                (
                                    "preview_text",
                                    wagtail.blocks.CharBlock(
                                        help_text="The text to display when the accordion is collapsed",
                                        required=False,
                                    ),
                                ),
                                (
                                    "body",
                                    wagtail.blocks.RichTextBlock(
                                        features=[
                                            "h2",
                                            "h3",
                                            "bold",
                                            "italic",
                                            "image",
                                        ],
                                        help_text="The content shown when the accordion expanded",
                                    ),
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
                                        help_text="An optional link to display below the expanded content",
                                        required=False,
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                blank=True,
                verbose_name="Accordion blocks",
            ),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="pathways_information",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="pathways_summary",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="what_you_will_cover_blocks",
            field=wagtail.fields.StreamField(
                [
                    (
                        "accordion_block",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "heading",
                                    wagtail.blocks.CharBlock(
                                        help_text="A large heading diplayed next to the block",
                                        required=False,
                                    ),
                                ),
                                (
                                    "preview_text",
                                    wagtail.blocks.CharBlock(
                                        help_text="The text to display when the accordion is collapsed",
                                        required=False,
                                    ),
                                ),
                                (
                                    "body",
                                    wagtail.blocks.RichTextBlock(
                                        features=[
                                            "h2",
                                            "h3",
                                            "bold",
                                            "italic",
                                            "image",
                                        ],
                                        help_text="The content shown when the accordion expanded",
                                    ),
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
                                        help_text="An optional link to display below the expanded content",
                                        required=False,
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                blank=True,
                verbose_name="Accordion blocks",
            ),
        ),
        migrations.AlterField(
            model_name="programmepage",
            name="related_content_title",
            field=models.CharField(
                blank=True,
                help_text="Large title displayed above the related content items, e.g. 'More opportunities to study at the RCA'",
                max_length=120,
            ),
        ),
    ]
