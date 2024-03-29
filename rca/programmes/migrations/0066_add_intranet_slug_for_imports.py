# Generated by Django 3.1.10 on 2021-10-26 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0065_merge_20210910_1128"),
    ]

    operations = [
        migrations.AddField(
            model_name="programmepage",
            name="intranet_slug",
            field=models.SlugField(
                blank=True,
                help_text="In order to import events and news to the intranet and relate them to this programme, this             slug value should match the value of the slug on the Category page on the intranet",
            ),
        ),
    ]
