# Generated by Django 2.2.12 on 2020-05-02 13:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "0041_group_collection_permissions_verbose_name_plural"),
        ("landingpages", "0011_swap_for_page_chooser"),
    ]

    operations = [
        migrations.RemoveField(model_name="landingpage", name="highlights_link_text"),
        migrations.RemoveField(model_name="landingpage", name="highlights_link_url"),
        migrations.AddField(
            model_name="landingpage",
            name="highlights_page_link",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailcore.Page",
            ),
        ),
    ]
