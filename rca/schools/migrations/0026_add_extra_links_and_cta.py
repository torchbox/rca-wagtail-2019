# Generated by Django 2.2.12 on 2021-02-11 15:20

import wagtail.blocks
import wagtail.fields
from django.db import migrations

import rca.navigation.models


class Migration(migrations.Migration):

    dependencies = [
        ("schools", "0025_dont_allow_blank_page_references"),
    ]

    operations = [
        migrations.AddField(
            model_name="schoolpage",
            name="about_cta_block",
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
                verbose_name="CTA",
            ),
        ),
        migrations.AddField(
            model_name="schoolpage",
            name="about_external_links",
            field=wagtail.fields.StreamField(
                [
                    (
                        "link",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "url",
                                    rca.navigation.models.URLOrRelativeURLBLock(
                                        required=False
                                    ),
                                ),
                                (
                                    "page",
                                    wagtail.blocks.PageChooserBlock(
                                        required=False
                                    ),
                                ),
                                (
                                    "title",
                                    wagtail.blocks.CharBlock(
                                        help_text="Leave blank to use the page's own title, required if using a URL",
                                        required=False,
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                blank=True,
                verbose_name="External links",
            ),
        ),
    ]
