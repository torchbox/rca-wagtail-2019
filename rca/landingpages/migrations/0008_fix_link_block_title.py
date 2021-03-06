# Generated by Django 2.2.12 on 2020-04-29 14:43

import django.db.models.deletion
import wagtail.core.blocks
import wagtail.core.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("landingpages", "0007_add_cta")]

    operations = [
        migrations.AlterField(
            model_name="landingpage",
            name="contact_image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.CustomImage",
            ),
        ),
        migrations.AlterField(
            model_name="landingpage",
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
                            ]
                        ),
                    )
                ],
                blank=True,
            ),
        ),
    ]
