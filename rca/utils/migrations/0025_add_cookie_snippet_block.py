# Generated by Django 3.2.16 on 2023-11-08 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0024_alter_legacysitetag_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='CookieButtonSnippet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
            ],
        ),
    ]