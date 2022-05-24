# Generated by Django 3.2.11 on 2022-02-03 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shortcourses", "0030_add_contact_fields"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="shortcoursepage", name="access_planit_course_id",
        ),
        migrations.AlterField(
            model_name="shortcoursemanualdate",
            name="booking_link",
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name="shortcoursemanualdate",
            name="cost",
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="shortcoursemanualdate",
            name="end_date",
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name="shortcoursemanualdate",
            name="start_date",
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name="shortcoursepage",
            name="application_form_url",
            field=models.URLField(
                blank=True,
                help_text="The URL of the application form. This will be a direct link and won't open the modal",
            ),
        ),
        migrations.AlterField(
            model_name="shortcoursepage",
            name="manual_registration_url",
            field=models.URLField(
                blank=True, help_text="The register interest link shown in the modal"
            ),
        ),
        migrations.AlterField(
            model_name="shortcoursepage",
            name="show_register_link",
            field=models.BooleanField(
                default=1,
                help_text="If selected, an automatic 'Register your interest' link will be visible in the key details section",
            ),
        ),
    ]