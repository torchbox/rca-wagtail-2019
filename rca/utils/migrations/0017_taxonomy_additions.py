# Generated by Django 2.2.12 on 2020-09-30 08:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("utils", "0016_merge_22211127_0750"),
    ]

    operations = [
        migrations.CreateModel(
            name="SluggedTaxonomy",
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
            name="ResearchTheme",
            fields=[
                (
                    "sluggedtaxonomy_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="utils.SluggedTaxonomy",
                    ),
                ),
            ],
            bases=("utils.sluggedtaxonomy",),
        ),
        migrations.CreateModel(
            name="Sector",
            fields=[
                (
                    "sluggedtaxonomy_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="utils.SluggedTaxonomy",
                    ),
                ),
            ],
            bases=("utils.sluggedtaxonomy",),
        ),
    ]
