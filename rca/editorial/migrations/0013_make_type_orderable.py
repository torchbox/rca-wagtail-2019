# Generated by Django 3.1.10 on 2021-07-23 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("editorial", "0012_relatededitorialpage"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="editorialpagetypeplacement",
            options={"ordering": ["sort_order"]},
        ),
        migrations.AddField(
            model_name="editorialpagetypeplacement",
            name="sort_order",
            field=models.IntegerField(blank=True, editable=False, null=True),
        ),
    ]
