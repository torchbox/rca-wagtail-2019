# Generated by Django 2.2.12 on 2021-01-21 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("schools", "0021_add_page_option_to_link_block"),
    ]

    operations = [
        migrations.AddField(
            model_name="schoolpage",
            name="link_to_open_days",
            field=models.URLField(blank=True),
        ),
        migrations.DeleteModel(
            name="OpenDayLink",
        ),
    ]
