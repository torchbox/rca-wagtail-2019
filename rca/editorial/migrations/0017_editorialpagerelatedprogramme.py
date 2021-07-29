# Generated by Django 3.1.10 on 2021-07-26 15:45

import django.db.models.deletion
import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "0062_comment_models_and_pagesubscription"),
        ("editorial", "0016_adds_contact_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="EditorialPageRelatedProgramme",
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
                        related_name="related_programmes",
                        to="editorial.editorialpage",
                    ),
                ),
            ],
            options={"ordering": ["sort_order"], "abstract": False,},
        ),
    ]
