# Generated by Django 2.2.9 on 2020-04-15 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("shortcourses", "0006_add_short_course_details")]

    operations = [
        migrations.AlterField(
            model_name="shortcoursepage",
            name="access_planit_course_id",
            field=models.IntegerField(),
        )
    ]
