# Generated by Django 2.2.19 on 2021-04-12 13:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("research", "0016_stop_allowing_blank_pages"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="researchcentrepage", name="hero_colour_option",
        ),
    ]
