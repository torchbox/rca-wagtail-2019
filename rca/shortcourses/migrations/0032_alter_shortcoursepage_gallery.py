# Generated by Django 3.2.11 on 2022-05-24 09:22

from django.db import migrations
import wagtail.blocks
import wagtail.fields
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.images.blocks
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("shortcourses", "0031_remove_access_planit"),
    ]

    operations = [
        migrations.AlterField(
            model_name='shortcoursepage',
            name='gallery',
            field=wagtail.fields.StreamField([('slide', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock()), ('author', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('course', wagtail.blocks.CharBlock(required=False)), ('document', wagtail.documents.blocks.DocumentChooserBlock(help_text='Maximum file size: 10MB', required=False)), ('video_embed', wagtail.embeds.blocks.EmbedBlock(help_text='Add a YouTube or Vimeo video URL', required=False)), ('audio_embed', wagtail.embeds.blocks.EmbedBlock(help_text='Add a Soundcloud URL', required=False))]))], blank=True, verbose_name='Gallery'),
        ),
    ]
