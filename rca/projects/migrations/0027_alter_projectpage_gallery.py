# Generated by Django 3.2.11 on 2022-05-23 14:42

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0026_alter_projectpage_specification_document_link_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectpage',
            name='gallery',
            field=wagtail.core.fields.StreamField([('slide', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock()), ('author', wagtail.core.blocks.CharBlock(required=False)), ('link', wagtail.core.blocks.URLBlock(required=False)), ('course', wagtail.core.blocks.CharBlock(required=False)), ('document', wagtail.documents.blocks.DocumentChooserBlock(help_text='Recommended maximum file size: 10MB', required=False)), ('video_embed', wagtail.embeds.blocks.EmbedBlock(help_text='Add a YouTube or Vimeo video URL', required=False)), ('audio_embed', wagtail.embeds.blocks.EmbedBlock(help_text='Add a Soundcloud URL', required=False))]))], blank=True, verbose_name='Gallery'),
        ),
    ]