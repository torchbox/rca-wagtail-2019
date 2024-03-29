# Generated by Django 4.2.9 on 2024-01-16 07:35

import wagtail.images.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0005_wagtail_image_field"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rendition",
            name="file",
            field=wagtail.images.models.WagtailImageField(
                height_field="height",
                storage=wagtail.images.models.get_rendition_storage,
                upload_to=wagtail.images.models.get_rendition_upload_to,
                width_field="width",
            ),
        ),
    ]
