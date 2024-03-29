# Generated by Django 3.1.10 on 2021-07-15 13:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("utils", "0020_add_tap_widget_snippet"),
        ("programmes", "0062_add_subject_slugs"),
    ]

    operations = [
        migrations.AddField(
            model_name="programmepage",
            name="tap_widget",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="utils.tapwidgetsnippet",
            ),
        ),
    ]
