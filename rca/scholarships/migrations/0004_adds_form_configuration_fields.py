# Generated by Django 3.1.14 on 2021-12-23 15:02

import wagtail.blocks
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scholarships", "0003_adds_body_content_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="scholarshipslistingpage",
            name="characteristics_disclaimer",
            field=models.CharField(
                blank=True,
                help_text="A small disclaimer shown just above the scholarships listing.",
                max_length=250,
            ),
        ),
        migrations.AddField(
            model_name="scholarshipslistingpage",
            name="cta_block",
            field=wagtail.fields.StreamField(
                [
                    (
                        "call_to_action",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "title",
                                    wagtail.blocks.CharBlock(
                                        help_text="A large heading diplayed at the top of block",
                                        required=False,
                                    ),
                                ),
                                (
                                    "description",
                                    wagtail.blocks.CharBlock(required=False),
                                ),
                                (
                                    "page",
                                    wagtail.blocks.PageChooserBlock(
                                        required=False
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
                            ],
                            label="text promo",
                        ),
                    )
                ],
                blank=True,
                verbose_name="Call to action",
            ),
        ),
        migrations.AddField(
            model_name="scholarshipslistingpage",
            name="form_introduction",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="scholarshipslistingpage",
            name="key_details",
            field=wagtail.fields.RichTextField(blank=True),
        ),
    ]
