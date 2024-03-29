# Generated by Django 3.1.10 on 2021-07-23 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("editorial", "0009_add_gallery_block"),
    ]

    operations = [
        migrations.AddField(
            model_name="editorialpage",
            name="download_assets_heading",
            field=models.CharField(
                blank=True,
                help_text="The heading text displayed above download link",
                max_length=125,
            ),
        ),
        migrations.AddField(
            model_name="editorialpage",
            name="download_assets_link_title",
            field=models.CharField(
                blank=True,
                help_text="The text displayed as the download link",
                max_length=125,
            ),
        ),
        migrations.AddField(
            model_name="editorialpage",
            name="download_assets_url",
            field=models.URLField(blank=True),
        ),
    ]
