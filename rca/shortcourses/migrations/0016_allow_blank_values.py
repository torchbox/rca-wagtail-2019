# Generated by Django 2.2.12 on 2020-08-03 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shortcourses", "0015_add_subject_relationship"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shortcourserelatedstaff",
            name="first_name",
            field=models.CharField(blank=True, max_length=125),
        ),
        migrations.AlterField(
            model_name="shortcourserelatedstaff",
            name="surname",
            field=models.CharField(blank=-1, max_length=125),
        ),
    ]
