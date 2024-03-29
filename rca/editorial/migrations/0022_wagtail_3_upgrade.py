# Generated by Django 3.2.14 on 2022-07-13 16:58

import wagtail.blocks
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("editorial", "0021_alter_editorialpage_gallery"),
    ]

    operations = [
        migrations.AlterField(
            model_name="editorialpage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    ("image", wagtail.images.blocks.ImageChooserBlock()),
                    (
                        "heading",
                        wagtail.blocks.CharBlock(
                            form_classname="full title",
                            icon="title",
                            template="patterns/molecules/streamfield/blocks/heading_block.html",
                        ),
                    ),
                    ("paragraph", wagtail.blocks.RichTextBlock()),
                    ("embed", wagtail.embeds.blocks.EmbedBlock()),
                    (
                        "quote",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "quote",
                                    wagtail.blocks.CharBlock(
                                        form_classname="title",
                                        help_text="Enter quote text only, there is no need to add quotation marks",
                                    ),
                                ),
                                ("author", wagtail.blocks.CharBlock(required=False)),
                                ("job_title", wagtail.blocks.CharBlock(required=False)),
                            ]
                        ),
                    ),
                    (
                        "jw_video",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "title",
                                    wagtail.blocks.CharBlock(
                                        help_text="Optional title to identify the video. Not shown on the page.",
                                        required=False,
                                    ),
                                ),
                                (
                                    "video_url",
                                    wagtail.blocks.URLBlock(
                                        help_text="The URL of the video to show.",
                                        max_length=1000,
                                    ),
                                ),
                                (
                                    "poster_image",
                                    wagtail.images.blocks.ImageChooserBlock(
                                        help_text="The poster image to show as a placeholder for the video. For best results use an image 1920x1080 pixels"
                                    ),
                                ),
                            ]
                        ),
                    ),
                ],
                use_json_field=True,
            ),
        ),
        migrations.AlterField(
            model_name="editorialpage",
            name="cta_block",
            field=wagtail.fields.StreamField(
                [
                    (
                        "call_to_action",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "title",
                                    wagtail.blocks.CharBlock(
                                        help_text="A large heading diplayed at the top of block",
                                        required=False,
                                    ),
                                ),
                                (
                                    "description",
                                    wagtail.blocks.CharBlock(required=False),
                                ),
                                (
                                    "page",
                                    wagtail.blocks.PageChooserBlock(required=False),
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
                                                wagtail.blocks.URLBlock(required=False),
                                            ),
                                        ],
                                        help_text="An optional link to display below the expanded content",
                                        required=False,
                                    ),
                                ),
                            ],
                            label="text promo",
                        ),
                    )
                ],
                blank=True,
                use_json_field=True,
                verbose_name="Text promo",
            ),
        ),
        migrations.AlterField(
            model_name="editorialpage",
            name="gallery",
            field=wagtail.fields.StreamField(
                [
                    (
                        "slide",
                        wagtail.blocks.StructBlock(
                            [
                                ("title", wagtail.blocks.CharBlock(required=False)),
                                ("image", wagtail.images.blocks.ImageChooserBlock()),
                                ("author", wagtail.blocks.CharBlock(required=False)),
                                ("link", wagtail.blocks.URLBlock(required=False)),
                                ("course", wagtail.blocks.CharBlock(required=False)),
                                (
                                    "document",
                                    wagtail.documents.blocks.DocumentChooserBlock(
                                        help_text="Maximum file size: 10MB",
                                        required=False,
                                    ),
                                ),
                                (
                                    "video_embed",
                                    wagtail.embeds.blocks.EmbedBlock(
                                        help_text="Add a YouTube or Vimeo video URL",
                                        required=False,
                                    ),
                                ),
                                (
                                    "audio_embed",
                                    wagtail.embeds.blocks.EmbedBlock(
                                        help_text="Add a Soundcloud URL", required=False
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                blank=True,
                use_json_field=True,
                verbose_name="Gallery",
            ),
        ),
        migrations.AlterField(
            model_name="editorialpage",
            name="more_information",
            field=wagtail.fields.StreamField(
                [
                    (
                        "accordion_block",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "heading",
                                    wagtail.blocks.CharBlock(
                                        help_text="A large heading diplayed next to the block",
                                        required=False,
                                    ),
                                ),
                                (
                                    "preview_text",
                                    wagtail.blocks.CharBlock(
                                        help_text="The text to display when the accordion is collapsed",
                                        required=False,
                                    ),
                                ),
                                (
                                    "body",
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
                                        ],
                                        help_text="The content shown when the accordion expanded",
                                    ),
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
                                                wagtail.blocks.URLBlock(required=False),
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
                use_json_field=True,
                verbose_name="More information",
            ),
        ),
        migrations.AlterField(
            model_name="editorialpage",
            name="quote_carousel",
            field=wagtail.fields.StreamField(
                [
                    (
                        "quote",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "quote",
                                    wagtail.blocks.CharBlock(
                                        form_classname="title",
                                        help_text="Enter quote text only, there is no need to add quotation marks",
                                    ),
                                ),
                                ("author", wagtail.blocks.CharBlock(required=False)),
                                ("job_title", wagtail.blocks.CharBlock(required=False)),
                            ]
                        ),
                    )
                ],
                blank=True,
                use_json_field=True,
                verbose_name="Quote Carousel",
            ),
        ),
    ]
