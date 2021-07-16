from django.db import migrations, models

from rca.programmes.models import Subject


def update_subjects(apps, schema_editor):
    for item in Subject.objects.all():
        item.save()


class Migration(migrations.Migration):
    """Custom migration to populate slug values on existing subjects
    so the can be used as filters"""

    dependencies = [
        ("programmes", "0061_subject_slug"),
    ]

    operations = [
        migrations.RunPython(update_subjects),
    ]
