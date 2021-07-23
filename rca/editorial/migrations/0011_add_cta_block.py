# Generated by Django 3.1.10 on 2021-07-23 11:11

import wagtail.core.blocks
import wagtail.core.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("editorial", "0010_add_asset_download_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="editorialpage",
            name="cta_block",
            field=wagtail.core.fields.StreamField(
                [
                    (
                        "call_to_action",
                        wagtail.core.blocks.StructBlock(
                            [
                                (
                                    "title",
                                    wagtail.core.blocks.CharBlock(
                                        help_text="A large heading diplayed at the top of block",
                                        required=False,
                                    ),
                                ),
                                (
                                    "description",
                                    wagtail.core.blocks.CharBlock(required=False),
                                ),
                                (
                                    "page",
                                    wagtail.core.blocks.PageChooserBlock(
                                        required=False
                                    ),
                                ),
                                (
                                    "link",
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
                verbose_name="Text promo",
            ),
        ),
    ]