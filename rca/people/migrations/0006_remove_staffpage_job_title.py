# Generated by Django 2.2.12 on 2020-06-08 10:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0005_staffpagemanualrelatedstudents"),
    ]

    operations = [
        migrations.RemoveField(model_name="staffpage", name="job_title",),
    ]
