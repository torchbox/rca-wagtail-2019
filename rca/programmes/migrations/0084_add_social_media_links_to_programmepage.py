# Generated by Django 3.2.16 on 2023-11-21 16:37

import django.db.models.deletion
import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0083_merge_20230918_1445"),
    ]

    operations = [
        migrations.AddField(
            model_name="programmepage",
            name="social_media_links_title",
            field=models.CharField(
                blank=True,
                help_text="The title of the social media links section",
                max_length=120,
                verbose_name="Title",
            ),
        ),
        migrations.CreateModel(
            name="ProgramPageSocialMediaLinks",
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
                ("link_url", models.URLField(verbose_name="Link URL")),
                ("link_text", models.CharField(max_length=100)),
                (
                    "source_page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="social_media_links",
                        to="programmes.programmepage",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
    ]