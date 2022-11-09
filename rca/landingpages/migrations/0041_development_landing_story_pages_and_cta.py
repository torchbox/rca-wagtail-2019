# Generated by Django 3.1.10 on 2021-08-20 07:50

import django.db.models.deletion
import modelcluster.fields
import wagtail.blocks
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "0062_comment_models_and_pagesubscription"),
        ("landingpages", "0040_dev_related_pages_and_extra_cta"),
    ]

    operations = [
        migrations.AddField(
            model_name="developmentlandingpage",
            name="stories_cta_block",
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
                                    wagtail.blocks.PageChooserBlock(
                                        required=False
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
                                                wagtail.blocks.URLBlock(
                                                    required=False
                                                ),
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
                verbose_name="Text promo",
            ),
        ),
        migrations.AddField(
            model_name="developmentlandingpage",
            name="stories_intro",
            field=models.CharField(
                blank=True,
                help_text="Optional short text summary for the 'Stories' section",
                max_length=250,
                verbose_name="Stories section summary",
            ),
        ),
        migrations.AddField(
            model_name="developmentlandingpage",
            name="stories_link_target_url",
            field=models.URLField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="developmentlandingpage",
            name="stories_link_text",
            field=models.TextField(
                default="", help_text="The text do display for the link", max_length=120
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="DevelopmentLandingPageRelatedEditorialPage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                (
                    "page",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "source_page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="related_editorial_pages",
                        to="landingpages.developmentlandingpage",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
    ]
