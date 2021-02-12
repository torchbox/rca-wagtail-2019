# Generated by Django 2.2.12 on 2021-01-22 14:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shortcourses", "0023_allow_blank_values"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shortcoursepagerelatedprogramme",
            name="page",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="wagtailcore.Page",
            ),
        ),
        migrations.AlterField(
            model_name="shortcoursrelatedschoolsandresearchpages",
            name="page",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="wagtailcore.Page",
            ),
        ),
    ]
