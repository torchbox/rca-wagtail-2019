# Generated by Django 2.2.12 on 2020-05-04 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("guides", "0005_specifc_streamfield_for_guides")]

    operations = [
        migrations.AddField(
            model_name="guidepage",
            name="further_information_title",
            field=models.CharField(blank=True, max_length=120),
        )
    ]
