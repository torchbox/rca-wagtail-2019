# Generated by Django 2.2.12 on 2020-06-18 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("utils", "0013_legacysitetag_legacysitetaggedpage"),
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
