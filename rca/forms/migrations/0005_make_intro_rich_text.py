# Generated by Django 2.2.12 on 2021-03-17 15:07

import wagtail.core.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("forms", "0004_auto_20210311_1622"),
    ]

    operations = [
        migrations.AlterField(
            model_name="formpage",
            name="introduction",
            field=wagtail.core.fields.RichTextField(blank=True),
        ),
    ]