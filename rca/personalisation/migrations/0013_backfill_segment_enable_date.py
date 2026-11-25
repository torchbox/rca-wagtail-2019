from django.db import migrations
from django.db.models import F


def backfill_enable_date(apps, schema_editor):
    # The receiver that sets enable_date never ran on Django 5.2, because the
    # package's AppConfig wasn't loaded. That left enabled segments with no
    # enable_date, so the admin said they had been active for 0 days. The
    # receiver only sets the date when the status changes, so these segments
    # would keep showing 0 even after the fix. Segments are enabled when
    # they're created, so create_date is the closest date we have.
    Segment = apps.get_model("wagtail_personalisation", "Segment")
    Segment.objects.filter(status="enabled", enable_date__isnull=True).update(
        enable_date=F("create_date")
    )


class Migration(migrations.Migration):
    dependencies = [
        ("personalisation", "0012_collapsiblenavigationctaexcludedpage_and_more"),
        (
            "wagtail_personalisation",
            "0026_alter_dayrule_segment_alter_devicerule_segment_and_more",
        ),
    ]

    operations = [
        # There's nothing to reverse: we can't tell which dates the migration
        # set and which the receiver set.
        migrations.RunPython(backfill_enable_date, migrations.RunPython.noop),
    ]
