# Generated by Django 2.2.12 on 2021-02-10 15:42

import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("schools", "0025_dont_allow_blank_page_references"),
    ]

    operations = [
        migrations.AlterField(
            model_name="schoolpage",
            name="collaborators",
            field=wagtail.core.fields.StreamField(
                [
                    (
                        "Collaborator",
                        wagtail.core.blocks.StructBlock(
                            [
                                ("image", wagtail.images.blocks.ImageChooserBlock()),
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
                                        ]
                                    ),
                                ),
                                (
                                    "page",
                                    wagtail.core.blocks.PageChooserBlock(
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
        migrations.AlterField(
            model_name="schoolpage",
            name="research_collaborators",
            field=wagtail.core.fields.StreamField(
                [
                    (
                        "Collaborator",
                        wagtail.core.blocks.StructBlock(
                            [
                                ("image", wagtail.images.blocks.ImageChooserBlock()),
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
                                        ]
                                    ),
                                ),
                                (
                                    "page",
                                    wagtail.core.blocks.PageChooserBlock(
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
        migrations.AlterField(
            model_name="schoolpage",
            name="research_projects_text",
            field=wagtail.core.fields.RichTextField(blank=True),
        ),
    ]
