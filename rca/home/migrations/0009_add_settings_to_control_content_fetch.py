# Generated by Django 3.1.10 on 2021-08-25 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0008_switch_partnerships_block_mehotds"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepage",
            name="use_api_for_alumni_stories",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="homepage",
            name="use_api_for_news_and_events",
            field=models.BooleanField(default=True),
        ),
    ]
