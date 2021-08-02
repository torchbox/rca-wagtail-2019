# Generated by Django 3.1.10 on 2021-07-27 11:57

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ("research", "0017_remove_hero_colour_options"),
        ("schools", "0030_merge_20210720_0923"),
        ("people", "0028_studentpage_student_user_image_collection"),
        ("events", "0007_event_footer_cta_20210726_1201"),
    ]

    operations = [
        migrations.CreateModel(
            name="EventDetailPageRelatedSchool",
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
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                (
                    "school",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="schools.schoolpage",
                    ),
                ),
                (
                    "source_page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="schools",
                        to="events.eventdetailpage",
                    ),
                ),
            ],
            options={"ordering": ["sort_order"],},
        ),
        migrations.CreateModel(
            name="EventDetailPageRelatedResearchCentre",
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
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                (
                    "research_centre",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="research.researchcentrepage",
                    ),
                ),
                (
                    "source_page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="research_centres",
                        to="events.eventdetailpage",
                    ),
                ),
            ],
            options={"ordering": ["sort_order"],},
        ),
        migrations.CreateModel(
            name="EventDetailPageRelatedDirectorate",
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
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                (
                    "directorate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="people.directorate",
                    ),
                ),
                (
                    "source_page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="directorates",
                        to="events.eventdetailpage",
                    ),
                ),
            ],
            options={"ordering": ["sort_order"],},
        ),
    ]