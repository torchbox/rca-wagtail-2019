# Generated by Django 2.2.12 on 2021-03-08 17:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0003_extends_image_fields"),
        ("people", "0019_studentpagegalleryslide"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentpagegalleryslide",
            name="author",
            field=models.CharField(default="", max_length=120),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="studentpagegalleryslide",
            name="image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.CustomImage",
            ),
        ),
    ]
