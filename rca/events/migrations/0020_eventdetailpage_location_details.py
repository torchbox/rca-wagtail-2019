# Generated by Django 3.2.14 on 2022-12-06 16:20

from django.db import migrations
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0019_wagtail_3_upgrade'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventdetailpage',
            name='location_details',
            field=wagtail.fields.RichTextField(blank=True),
        ),
    ]
