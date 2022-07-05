# Generated by Django 2.2.12 on 2021-02-23 15:30

import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.images.blocks
import wagtail.snippets.blocks
from django.db import migrations


class Migration(migrations.Migration):

    replaces = [
        ("standardpages", "0006_embed_video_help_text"),
        ("standardpages", "0007_embed_video_help_text"),
    ]

    dependencies = [
        ("standardpages", "0005_stop_allowing_blank_pages"),
    ]

    operations = [
        migrations.AlterField(
            model_name="informationpage",
            name="body",
            field=wagtail.core.fields.StreamField(
                [
                    (
                        "heading",
                        wagtail.core.blocks.CharBlock(
                            form_classname="full title",
                            icon="title",
                            template="patterns/molecules/streamfield/blocks/heading_block.html",
                        ),
                    ),
                    ("paragraph", wagtail.core.blocks.RichTextBlock()),
                    (
                        "image",
                        wagtail.core.blocks.StructBlock(
                            [
                                ("image", wagtail.images.blocks.ImageChooserBlock()),
                                (
                                    "caption",
                                    wagtail.core.blocks.CharBlock(required=False),
                                ),
                            ]
                        ),
                    ),
                    (
                        "quote",
                        wagtail.core.blocks.StructBlock(
                            [
                                (
                                    "quote",
                                    wagtail.core.blocks.CharBlock(
                                        form_classname="title",
                                        help_text="Enter quote text only, there is no need to add quotation marks",
                                    ),
                                ),
                                (
                                    "author",
                                    wagtail.core.blocks.CharBlock(required=False),
                                ),
                                (
                                    "job_title",
                                    wagtail.core.blocks.CharBlock(required=False),
                                ),
                            ]
                        ),
                    ),
                    (
                        "embed",
                        wagtail.embeds.blocks.EmbedBlock(
                            help_text="Add a URL from these providers: YouTube, Vimeo, SoundCloud, Twitter.",
                            label="Embed video",
                        ),
                    ),
                    (
                        "call_to_action",
                        wagtail.snippets.blocks.SnippetChooserBlock(
                            "utils.CallToActionSnippet",
                            template="patterns/molecules/streamfield/blocks/call_to_action_block.html",
                        ),
                    ),
                    (
                        "document",
                        wagtail.core.blocks.StructBlock(
                            [
                                (
                                    "document",
                                    wagtail.documents.blocks.DocumentChooserBlock(),
                                ),
                                (
                                    "title",
                                    wagtail.core.blocks.CharBlock(required=False),
                                ),
                            ]
                        ),
                    ),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="informationpage",
            name="body",
            field=wagtail.core.fields.StreamField(
                [
                    (
                        "heading",
                        wagtail.core.blocks.CharBlock(
                            form_classname="full title",
                            icon="title",
                            template="patterns/molecules/streamfield/blocks/heading_block.html",
                        ),
                    ),
                    ("paragraph", wagtail.core.blocks.RichTextBlock()),
                    (
                        "image",
                        wagtail.core.blocks.StructBlock(
                            [
                                ("image", wagtail.images.blocks.ImageChooserBlock()),
                                (
                                    "caption",
                                    wagtail.core.blocks.CharBlock(required=False),
                                ),
                            ]
                        ),
                    ),
                    (
                        "quote",
                        wagtail.core.blocks.StructBlock(
                            [
                                (
                                    "quote",
                                    wagtail.core.blocks.CharBlock(
                                        form_classname="title",
                                        help_text="Enter quote text only, there is no need to add quotation marks",
                                    ),
                                ),
                                (
                                    "author",
                                    wagtail.core.blocks.CharBlock(required=False),
                                ),
                                (
                                    "job_title",
                                    wagtail.core.blocks.CharBlock(required=False),
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
                        wagtail.core.blocks.StructBlock(
                            [
                                (
                                    "document",
                                    wagtail.documents.blocks.DocumentChooserBlock(),
                                ),
                                (
                                    "title",
                                    wagtail.core.blocks.CharBlock(required=False),
                                ),
                            ]
                        ),
                    ),
                ]
            ),
        ),
    ]
