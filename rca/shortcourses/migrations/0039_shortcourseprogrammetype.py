# Generated by Django 4.2.16 on 2025-01-14 14:45

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0094_migrate_programme_type_to_programme_types"),
        ("shortcourses", "0038_shortcoursepage_dates"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShortCourseProgrammeType",
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
                        related_name="programme_types",
                        to="shortcourses.shortcoursepage",
                    ),
                ),
                (
                    "programme_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="short_course",
                        to="programmes.programmetype",
                    ),
                ),
            ],
        ),
    ]