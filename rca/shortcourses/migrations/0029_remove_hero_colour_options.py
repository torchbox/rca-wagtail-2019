# Generated by Django 2.2.19 on 2021-04-12 13:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("shortcourses", "0028_helptext_override_ap_modal"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="shortcoursepage", name="hero_colour_option",
        ),
    ]
