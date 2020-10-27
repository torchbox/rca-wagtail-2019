# Generated by Django 2.2.12 on 2020-10-27 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("utils", "0016_merge_22211127_0750"),
    ]

    operations = [
        migrations.AlterField(
            model_name="legacysitetag",
            name="name",
            field=models.CharField(max_length=100, unique=True, verbose_name="Name"),
        ),
        migrations.AlterField(
            model_name="legacysitetag",
            name="slug",
            field=models.SlugField(max_length=100, unique=True, verbose_name="Slug"),
        ),
    ]
