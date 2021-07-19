from django.db import migrations, models


def update_subjects(apps, schema_editor):
    Subject = apps.get_model("programmes", "Subject")
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
