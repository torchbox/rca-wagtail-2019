# Generated by Django 2.2.12 on 2021-02-09 15:07

import wagtail.blocks
import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0012_adds_student_page_base_fields_and_related_models"),
    ]

    operations = [
        migrations.AlterField(
            model_name="studentpage",
            name="social_links",
            field=wagtail.fields.StreamField(
                [
                    (
                        "Link",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "title",
                                    wagtail.blocks.CharBlock(required=False),
                                ),
                                ("url", wagtail.blocks.URLBlock(required=False)),
                            ],
                            required=False,
                        ),
                    )
                ],
                blank=True,
                verbose_name="Personal links",
            ),
        ),
    ]
