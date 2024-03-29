# Generated by Django 3.1.10 on 2021-08-11 12:49

import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("landingpages", "0033_alumnilandingpage"),
    ]

    operations = [
        migrations.AddField(
            model_name="alumnilandingpage",
            name="collaborators",
            field=wagtail.fields.StreamField(
                [
                    (
                        "Collaborator",
                        wagtail.blocks.StructBlock(
                            [
                                ("image", wagtail.images.blocks.ImageChooserBlock()),
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
                                        ]
                                    ),
                                ),
                                (
                                    "page",
                                    wagtail.blocks.PageChooserBlock(
                                        required=False
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                blank=True,
                help_text="You can add up to 9 collaborators. Minimum 200 x 200 pixels.             Aim for logos that sit on either a white or transparent background.",
            ),
        ),
    ]
