# Generated by Django 3.2.12 on 2022-07-11 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("landingpages", "0044_merge_20210910_1128"),
    ]

    operations = [
        migrations.AddField(
            model_name="landingpage",
            name="news_and_events_link_target_url",
            field=models.URLField(
                blank=True, help_text="Add a link to view all news and events"
            ),
        ),
        migrations.AddField(
            model_name="landingpage",
            name="news_and_events_link_text",
            field=models.TextField(
                blank=True,
                help_text="The text to display for the 'View all news and events' link",
                max_length=120,
            ),
        ),
        migrations.AddField(
            model_name="landingpage",
            name="news_and_events_title",
            field=models.TextField(
                blank=True,
                help_text="The title to display above the news and events listing",
                max_length=120,
            ),
        ),
    ]
