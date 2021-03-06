# Generated by Django 2.2.9 on 2020-01-16 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("images", "0002_customimage_file_hash")]

    operations = [
        migrations.AddField(
            model_name="customimage",
            name="alt",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="customimage",
            name="creator",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="customimage",
            name="dimensions",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="customimage",
            name="medium",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="customimage",
            name="permission",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="customimage",
            name="photographer",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="customimage",
            name="year",
            field=models.CharField(blank=True, max_length=4),
        ),
    ]
