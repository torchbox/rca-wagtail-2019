# Generated by Django 3.2.16 on 2023-08-15 09:57

import django.db.models.deletion
import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0074_merge_20230302_0516"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProgrammeStudyMode",
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
            ],
        ),
        migrations.CreateModel(
            name="ProgrammeStudyModeProgrammePage",
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
                        related_name="programme_study_modes",
                        to="programmes.programmepage",
                    ),
                ),
                (
                    "programme_study_mode",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="programmes.programmestudymode",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="programmestudymodeprogrammepage",
            constraint=models.UniqueConstraint(
                fields=("page", "programme_study_mode"),
                name="unique_programme_study_mode_per_programme_page",
            ),
        ),
    ]