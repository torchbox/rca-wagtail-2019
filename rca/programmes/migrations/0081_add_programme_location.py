# Generated by Django 3.2.16 on 2023-08-18 04:24

import django.db.models.deletion
import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0080_add_alumni_cta_link_to_programmepageglobalfieldssettings"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProgrammeLocation",
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
                ("title", models.CharField(max_length=128)),
                ("slug", models.SlugField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="ProgrammeLocationProgrammePage",
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
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="programme_locations",
                        to="programmes.programmepage",
                    ),
                ),
                (
                    "programme_location",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="programmes.programmelocation",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="programmelocationprogrammepage",
            constraint=models.UniqueConstraint(
                fields=("page", "programme_location"),
                name="unique_programme_location_per_programme_page",
            ),
        ),
    ]