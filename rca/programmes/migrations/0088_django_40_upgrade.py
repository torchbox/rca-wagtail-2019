# Generated by Django 4.0.10 on 2024-01-16 07:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("taggit", "0005_auto_20220424_2025"),
        ("programmes", "0087_merge_20231124_1110"),
    ]

    operations = [
        migrations.AlterField(
            model_name="programmepagetag",
            name="tag",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(app_label)s_%(class)s_items",
                to="taggit.tag",
            ),
        ),
    ]