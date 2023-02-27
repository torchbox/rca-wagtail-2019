# Generated by Django 3.1.10 on 2021-07-23 08:55

import wagtail.blocks
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("editorial", "0007_alterations_to_body_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="editorialpage",
            name="more_information",
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
                                            "ul",
                                            "ol",
                                            "link",
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
                verbose_name="More information",
            ),
        ),
        migrations.AddField(
            model_name="editorialpage",
            name="more_information_title",
            field=models.CharField(default="More information", max_length=80),
        ),
    ]
