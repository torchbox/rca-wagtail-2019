# Generated by Django 3.1.10 on 2021-06-06 03:53

import django.db.models.deletion
import wagtail.blocks
import wagtail.fields
import wagtail.embeds.blocks
import wagtail.images.blocks
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0028_studentpage_student_user_image_collection"),
        ("editorial", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="editorialpage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    ("heading", wagtail.blocks.CharBlock()),
                    ("paragraph", wagtail.blocks.RichTextBlock()),
                    ("image", wagtail.images.blocks.ImageChooserBlock()),
                    ("embed", wagtail.embeds.blocks.EmbedBlock()),
                ],
                blank=True,
            ),
        ),
    ]
