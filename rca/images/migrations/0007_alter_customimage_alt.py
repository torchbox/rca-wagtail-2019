# Generated by Django 4.2.11 on 2024-05-29 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0006_django_42_upgrade"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customimage",
            name="alt",
            field=models.CharField(max_length=255),
        ),
    ]