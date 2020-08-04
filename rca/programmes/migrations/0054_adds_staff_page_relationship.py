# Generated by Django 2.2.12 on 2020-08-03 18:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "0045_assign_unlock_grouppagepermission"),
        ("programmes", "0053_merge_20200430_0923"),
    ]

    operations = [
        migrations.AddField(
            model_name="programpagerelatedstaff",
            name="page",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="wagtailcore.Page",
            ),
        ),
        migrations.AlterField(
            model_name="programpagerelatedstaff",
            name="name",
            field=models.CharField(blank=True, max_length=125),
        ),
    ]
