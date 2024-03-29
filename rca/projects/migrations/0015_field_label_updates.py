# Generated by Django 2.2.12 on 2020-06-18 12:04

import django.db.models.deletion
import wagtail.blocks
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0014_make_research_type_orderable"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projectpage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    (
                        "quote_block",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "quote",
                                    wagtail.blocks.CharBlock(
                                        classname="title",
                                        help_text="Enter quote text only, there is no need to add quotation marks",
                                    ),
                                ),
                                (
                                    "author",
                                    wagtail.blocks.CharBlock(required=False),
                                ),
                                (
                                    "job_title",
                                    wagtail.blocks.CharBlock(required=False),
                                ),
                            ]
                        ),
                    ),
                    (
                        "rich_text_block",
                        wagtail.blocks.RichTextBlock(
                            features=[
                                "h2",
                                "h3",
                                "bold",
                                "italic",
                                "image",
                                "ul",
                                "ol",
                                "link",
                            ]
                        ),
                    ),
                    (
                        "link_block",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "title",
                                    wagtail.blocks.CharBlock(required=False),
                                ),
                                ("url", wagtail.blocks.URLBlock(required=False)),
                            ]
                        ),
                    ),
                ],
                blank=True,
                verbose_name="Body copy",
            ),
        ),
        migrations.AlterField(
            model_name="projectpage",
            name="specification_document",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="documents.CustomDocument",
                verbose_name="Project PDF",
            ),
        ),
    ]
