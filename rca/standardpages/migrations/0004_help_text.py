# Generated by Django 2.2.12 on 2020-04-22 10:19

import wagtail.blocks
import wagtail.fields
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.images.blocks
import wagtail.snippets.blocks
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("standardpages", "0003_update_body_field")]

    operations = [
        migrations.AlterField(
            model_name="informationpage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    (
                        "heading",
                        wagtail.blocks.CharBlock(
                            classname="full title",
                            icon="title",
                            template="patterns/molecules/streamfield/blocks/heading_block.html",
                        ),
                    ),
                    ("paragraph", wagtail.blocks.RichTextBlock()),
                    (
                        "image",
                        wagtail.blocks.StructBlock(
                            [
                                ("image", wagtail.images.blocks.ImageChooserBlock()),
                                (
                                    "caption",
                                    wagtail.blocks.CharBlock(required=False),
                                ),
                            ]
                        ),
                    ),
                    (
                        "quote",
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
                    ("embed", wagtail.embeds.blocks.EmbedBlock()),
                    (
                        "call_to_action",
                        wagtail.snippets.blocks.SnippetChooserBlock(
                            "utils.CallToActionSnippet",
                            template="patterns/molecules/streamfield/blocks/call_to_action_block.html",
                        ),
                    ),
                    (
                        "document",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "document",
                                    wagtail.documents.blocks.DocumentChooserBlock(),
                                ),
                                (
                                    "title",
                                    wagtail.blocks.CharBlock(required=False),
                                ),
                            ]
                        ),
                    ),
                ]
            ),
        )
    ]
