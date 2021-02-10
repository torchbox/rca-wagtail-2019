# Generated by Django 2.2.12 on 2020-09-14 13:45

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0011_merge_20200622_1033'),
    ]

    operations = [
        migrations.CreateModel(
            name='Directorate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('slug', models.SlugField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='StaffPageDirectorate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('directorate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_staff', to='people.Directorate', verbose_name='Directorates')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_directorates', to='people.StaffPage')),
            ],
        ),
    ]
