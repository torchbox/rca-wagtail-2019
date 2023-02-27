# Generated by Django 3.2.14 on 2022-12-09 03:03

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('landingpages', '0045_wagtail_3_upgrade'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlumniLandingPageTeaser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=125)),
                ('summary', models.CharField(blank=True, max_length=250)),
                ('pages', wagtail.fields.StreamField([('Page', wagtail.blocks.StreamBlock([('page', wagtail.blocks.PageChooserBlock()), ('custom_teaser', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('meta', wagtail.blocks.CharBlock(help_text='Small tag value displayed below the title', required=False)), ('text', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock()), ('link', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('url', wagtail.blocks.URLBlock(required=False))], required=False))]))], max_num=6))], use_json_field=True)),
                ('source_page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='page_teasers', to='landingpages.alumnilandingpage')),
            ],
        ),
    ]
