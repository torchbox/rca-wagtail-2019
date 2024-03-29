# Generated by Django 2.2.12 on 2020-12-16 03:00

import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("schools", "0009_related_projects"),
    ]

    operations = [
        migrations.AddField(
            model_name="schoolpage",
            name="research_collaborators",
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
                            ]
                        ),
                    )
                ],
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="schoolpage",
            name="research_collaborators_heading",
            field=models.CharField(blank=True, max_length=120),
        ),
    ]
