# Generated by Django 4.0.10 on 2024-01-16 07:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("taggit", "0005_auto_20220424_2025"),
        ("shortcourses", "0035_add_embed_to_richtext_in_shortcoursepage_about"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shortcoursepagetag",
            name="tag",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(app_label)s_%(class)s_items",
                to="taggit.tag",
            ),
        ),
    ]
