# Generated by Django 3.2.11 on 2022-01-05 15:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scholarships", "0007_adds_scholarship_snippet_to_submission"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="scholarship",
            options={"ordering": ("title",)},
        ),
        migrations.AddField(
            model_name="scholarship",
            name="location",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="scholarships.scholarshiplocation",
            ),
        ),
    ]
