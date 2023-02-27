# Generated by Django 2.2.12 on 2020-10-28 20:37

import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0007_add_hero_image_credit"),
    ]

    operations = [
        migrations.AlterField(
            model_name="homepagepartnershipblock",
            name="slides",
            field=wagtail.fields.StreamField(
                [
                    (
                        "Page",
                        wagtail.blocks.StreamBlock(
                            [
                                ("page", wagtail.blocks.PageChooserBlock()),
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
    ]
