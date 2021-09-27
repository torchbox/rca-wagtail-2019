# Generated by Django 3.1.10 on 2021-07-08 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_customdocument_file_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customdocument',
            name='file',
            field=models.FileField(help_text='Maximum file size: 10MB.', upload_to='documents', verbose_name='file'),
        ),
    ]
