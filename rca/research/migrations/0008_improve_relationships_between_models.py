# Generated by Django 2.2.12 on 2020-06-03 11:12

import django.db.models.deletion
import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "0041_group_collection_permissions_verbose_name_plural"),
        ("research", "0007_add_curatable_project_relationship"),
    ]

    operations = [
        migrations.CreateModel(
            name="RelatedResearchCenterPage",
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
                        on_delete=django.db.models.deletion.CASCADE,
                        to="research.ResearchCentrePage",
                    ),
                ),
                (
                    "source_page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="related_research_centre_pages",
                        to="wagtailcore.Page",
                    ),
                ),
            ],
            options={"ordering": ["sort_order"], "abstract": False},
        )
    ]
