# Generated by Django 4.2.16 on 2025-01-14 14:25

from django.db import migrations

def migrate_programme_type_to_programme_types(apps, schema_editor):
    # Get the models
    ProgrammePage = apps.get_model("programmes", "ProgrammePage")
    ProgrammePageProgrammeType = apps.get_model("programmes", "ProgrammePageProgrammeType")

    for page in ProgrammePage.objects.all():
        if programme_type := page.programme_type:
            ProgrammePageProgrammeType.objects.create(
                page_id=page.id,
                programme_type=programme_type,
            )


class Migration(migrations.Migration):

    dependencies = [
        ("programmes", "0093_programmepageprogrammetype"),
    ]

    operations = [
        migrations.RunPython(migrate_programme_type_to_programme_types, reverse_code=migrations.RunPython.noop),
    ]