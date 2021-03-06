# Generated by Django 2.2.12 on 2020-05-04 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("research", "0005_merge_20200430_0956")]

    operations = [
        migrations.AddField(
            model_name="researchcentrepage",
            name="highlights_title",
            field=models.CharField(
                blank=True,
                help_text="The title value displayed above the Research highlights gallery showing project pages",
                max_length=120,
            ),
        )
    ]
