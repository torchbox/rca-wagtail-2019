# Generated by Django 2.2.12 on 2020-10-29 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shortcourses", "0021_auto_20201028_1931"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="shortcoursemanualdate", name="register_interest_link",
        ),
        migrations.AlterField(
            model_name="shortcoursemanualdate",
            name="booking_link",
            field=models.URLField(default=""),
            preserve_default=False,
        ),
    ]
