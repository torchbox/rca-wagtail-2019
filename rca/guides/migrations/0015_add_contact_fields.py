# Generated by Django 3.1.10 on 2021-07-14 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("guides", "0014_embed_video_help_text_squashed"),
    ]

    operations = [
        migrations.AddField(
            model_name="guidepage",
            name="contact_model_link_text",
            field=models.CharField(
                blank=True,
                help_text="Optional text for the linked url, form or email",
                max_length=120,
                verbose_name="Contact link text",
            ),
        ),
    ]
