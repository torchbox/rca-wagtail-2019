# Generated by Django 3.2.16 on 2023-08-15 14:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0004_wagtail_3_upgrade"),
        ("programmes", "0075_add_embed_to_accordion_block_richtext"),
    ]

    operations = [
        migrations.AddField(
            model_name="programmepage",
            name="requirements_video",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="requirements_video_caption",
            field=models.CharField(
                blank=True,
                help_text="The text dipsplayed next to the video play button",
                max_length=80,
            ),
        ),
        migrations.AddField(
            model_name="programmepage",
            name="requirements_video_preview_image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.customimage",
            ),
        ),
    ]
