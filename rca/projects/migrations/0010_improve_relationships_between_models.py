# Generated by Django 2.2.12 on 2020-06-03 11:12

import django.db.models.deletion
import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "0041_group_collection_permissions_verbose_name_plural"),
        ("schools", "0002_redefine_school_page"),
        ("projects", "0009_adds_featured_project_and_introduction"),
    ]

    operations = [
        migrations.CreateModel(
            name="RelatedProjectPage",
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
                        to="schools.SchoolPage",
                    ),
                ),
                (
                    "source_page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="related_project_pages",
                        to="wagtailcore.Page",
                    ),
                ),
            ],
            options={"ordering": ["sort_order"], "abstract": False},
        )
    ]
