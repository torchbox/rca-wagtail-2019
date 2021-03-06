# Generated by Django 2.2.12 on 2020-05-04 13:50

import wagtail.core.blocks
import wagtail.core.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("landingpages", "0012_swap_for_page_chooser")]

    operations = [
        migrations.AlterField(
            model_name="landingpage",
            name="page_list",
            field=wagtail.core.fields.StreamField(
                [
                    (
                        "page_list",
                        wagtail.core.blocks.StructBlock(
                            [
                                (
                                    "heading",
                                    wagtail.core.blocks.CharBlock(
                                        help_text="A large heading diplayed at the top of block",
                                        required=False,
                                    ),
                                ),
                                (
                                    "page",
                                    wagtail.core.blocks.StreamBlock(
                                        [
                                            (
                                                "page",
                                                wagtail.core.blocks.PageChooserBlock(),
                                            )
                                        ]
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
                                (
                                    "page_link",
                                    wagtail.core.blocks.PageChooserBlock(
                                        required=False
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                blank=True,
            ),
        )
    ]
