# Generated by Django 3.1.10 on 2021-07-14 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shortcourses", "0029_remove_hero_colour_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="shortcoursepage",
            name="contact_model_link_text",
            field=models.CharField(
                blank=True,
                help_text="Optional text for the linked url, form or email",
                max_length=120,
                verbose_name="Contact link text",
            ),
        ),
    ]