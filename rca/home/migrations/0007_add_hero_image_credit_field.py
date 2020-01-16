# Generated by Django 2.2.9 on 2020-01-16 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0006_add_link_to_slide"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepage",
            name="hero_image_credit",
            field=models.CharField(
                blank=True,
                help_text="Adding specific credit text here will         override the images meta data fields.",
                max_length=255,
            ),
        ),
    ]
