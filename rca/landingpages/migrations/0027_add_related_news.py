# Generated by Django 3.1.10 on 2021-07-22 08:14

import django.db.models.deletion
import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "0062_comment_models_and_pagesubscription"),
        ("landingpages", "0026_eelandingpage"),
    ]

    operations = [
        migrations.AddField(
            model_name="eelandingpage",
            name="news_link_target_url",
            field=models.URLField(null=True),
        ),
        migrations.AddField(
            model_name="eelandingpage",
            name="news_link_text",
            field=models.TextField(
                help_text="The text do display for the link", max_length=120, null=True
            ),
        ),
        migrations.CreateModel(
            name="EELandingPageRelatedEditorialPage",
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
                        to="landingpages.eelandingpage",
                    ),
                ),
            ],
            options={"ordering": ["sort_order"], "abstract": False,},
        ),
    ]
