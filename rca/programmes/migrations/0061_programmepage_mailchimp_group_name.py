# Generated by Django 2.2.12 on 2021-04-28 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0060_merge_20210429_1122"),
    ]

    operations = [
        migrations.AddField(
            model_name="programmepage",
            name="mailchimp_group_name",
            field=models.CharField(
                blank=True,
                help_text="This must match a group name under the category 'Programme of interest' E.G 'MA Animation'",
                max_length=255,
                null=True,
            ),
        ),
    ]