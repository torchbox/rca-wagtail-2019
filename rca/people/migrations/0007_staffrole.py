# Generated by Django 2.2.12 on 2020-06-08 16:01

import django.db.models.deletion
import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0053_merge_20200430_0923"),
        ("people", "0006_remove_staffpage_job_title"),
    ]

    operations = [
        migrations.CreateModel(
            name="StaffRole",
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
                ("role", models.CharField(max_length=128)),
                (
                    "custom_programme",
                    models.CharField(
                        blank=True,
                        help_text="Specify a custom programme page here if one does not exist",
                        max_length=128,
                    ),
                ),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="roles",
                        to="people.StaffPage",
                    ),
                ),
                (
                    "programme",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="related_programme",
                        to="programmes.ProgrammePage",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
    ]
