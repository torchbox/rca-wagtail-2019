# Generated by Django 2.2.12 on 2020-06-03 13:13

from django.db import migrations
import modelcluster.contrib.taggit


class Migration(migrations.Migration):

    dependencies = [
        ("utils", "0013_legacysitetag_legacysitetaggedpage"),
        ("landingpages", "0015_auto_20200506_1629"),
    ]

    operations = [
        migrations.AddField(
            model_name="landingpage",
            name="legacy_news_and_event_tags",
            field=modelcluster.contrib.taggit.ClusterTaggableManager(
                blank=True,
                help_text="Specify one or more tags to identify related news and events from the legacy site. A maximum of three items with the same combination of tags will then be displayed on the page.",
                through="utils.LegacySiteTaggedPage",
                to="utils.LegacySiteTag",
                verbose_name="Legacy news and event tags",
            ),
        )
    ]
