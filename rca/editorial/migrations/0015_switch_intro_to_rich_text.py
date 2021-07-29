# Generated by Django 3.1.10 on 2021-07-27 08:58

import wagtail.core.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("editorial", "0014_add_quote_block_to_body"),
    ]

    operations = [
        migrations.AlterField(
            model_name="editorialpage",
            name="introduction",
            field=wagtail.core.fields.RichTextField(
                blank=True, verbose_name="help text"
            ),
        ),
    ]
