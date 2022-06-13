# Generated by Django 3.2.12 on 2022-06-13 15:42

from django.db import migrations
import wagtail.blocks
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('shortcourses', '0032_alter_shortcoursepage_gallery'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shortcoursepage',
            name='about',
            field=wagtail.fields.StreamField([('accordion_block', wagtail.blocks.StructBlock([('heading', wagtail.blocks.CharBlock(help_text='A large heading diplayed next to the block', required=False)), ('preview_text', wagtail.blocks.CharBlock(help_text='The text to display when the accordion is collapsed', required=False)), ('body', wagtail.blocks.RichTextBlock(features=['h2', 'h3', 'bold', 'italic', 'image', 'ul', 'ol', 'link'], help_text='The content shown when the accordion expanded')), ('link', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('url', wagtail.blocks.URLBlock(required=False))], help_text='An optional link to display below the expanded content', required=False))]))], blank=True, use_json_field=True, verbose_name='About the course'),
        ),
        migrations.AlterField(
            model_name='shortcoursepage',
            name='external_links',
            field=wagtail.fields.StreamField([('link', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('url', wagtail.blocks.URLBlock(required=False))]))], blank=True, use_json_field=True, verbose_name='External Links'),
        ),
        migrations.AlterField(
            model_name='shortcoursepage',
            name='gallery',
            field=wagtail.fields.StreamField([('slide', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock()), ('author', wagtail.blocks.CharBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False)), ('course', wagtail.blocks.CharBlock(required=False)), ('document', wagtail.documents.blocks.DocumentChooserBlock(help_text='Maximum file size: 10MB', required=False)), ('video_embed', wagtail.embeds.blocks.EmbedBlock(help_text='Add a YouTube or Vimeo video URL', required=False)), ('audio_embed', wagtail.embeds.blocks.EmbedBlock(help_text='Add a Soundcloud URL', required=False))]))], blank=True, use_json_field=True, verbose_name='Gallery'),
        ),
        migrations.AlterField(
            model_name='shortcoursepage',
            name='quote_carousel',
            field=wagtail.fields.StreamField([('quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.CharBlock(form_classname='title', help_text='Enter quote text only, there is no need to add quotation marks')), ('author', wagtail.blocks.CharBlock(required=False)), ('job_title', wagtail.blocks.CharBlock(required=False))]))], blank=True, use_json_field=True, verbose_name='Quote carousel'),
        ),
    ]
