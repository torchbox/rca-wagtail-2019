# Generated by Django 2.2.4 on 2019-08-22 09:32

import django.db.models.deletion
import wagtail.blocks
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0002_customimage_file_hash"),
        ("programmes", "0007_add_fees_section_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="programmepage",
            name="apply_cta_link",
            field=models.URLField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="programmepage",
            name="apply_cta_text",
            field=models.CharField(default="", max_length=125),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="programmepage",
            name="apply_image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.CustomImage",
            ),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="apply_image_sub_title",
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="apply_image_title",
            field=models.CharField(blank=True, max_length=125),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="apply_title",
            field=models.CharField(default="Start your application", max_length=125),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="steps",
            field=wagtail.fields.StreamField(
                [
                    (
                        "step",
                        wagtail.blocks.StructBlock(
                            [
                                ("heading", wagtail.blocks.CharBlock()),
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
    ]
