# Generated by Django 3.2.12 on 2022-07-05 13:01

import django.db.models.deletion
import modelcluster.contrib.taggit
import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("taggit", "0004_alter_taggeditem_content_type_alter_taggeditem_tag"),
        ("shortcourses", "0032_alter_shortcoursepage_gallery"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShortCoursePageTag",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "content_object",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tagged_short_course_items",
                        to="shortcourses.shortcoursepage",
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shortcourses_shortcoursepagetag_items",
                        to="taggit.tag",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="shortcoursepage",
            name="tags",
            field=modelcluster.contrib.taggit.ClusterTaggableManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="shortcourses.ShortCoursePageTag",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
    ]