# Generated by Django 2.2.4 on 2019-08-14 08:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("standardpages", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="informationpagerelatedpage",
            name="page",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="wagtailcore.Page",
            ),
        )
    ]
