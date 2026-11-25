from datetime import datetime, timezone
from importlib import import_module

from django.apps import apps
from django.test import TestCase
from wagtail_personalisation.models import Segment

from rca.personalisation.factories import SegmentFactory

backfill_enable_date = import_module(
    "rca.personalisation.migrations.0013_backfill_segment_enable_date"
).backfill_enable_date

CREATED = datetime(2026, 3, 16, 15, 42, tzinfo=timezone.utc)


class BackfillEnableDateTest(TestCase):
    def make_segment(self, **kwargs):
        segment = SegmentFactory(**kwargs)
        # .update() skips the pre_save receiver and auto_now_add, so the
        # segment looks like one saved while the receiver wasn't connected.
        Segment.objects.filter(pk=segment.pk).update(
            create_date=CREATED,
            enable_date=kwargs.get("enable_date"),
            disable_date=kwargs.get("disable_date"),
        )
        return segment

    def test_enabled_segment_without_enable_date_gets_its_create_date(self):
        segment = self.make_segment(status=Segment.STATUS_ENABLED)

        backfill_enable_date(apps, None)
        segment.refresh_from_db()

        self.assertEqual(segment.enable_date, CREATED)
        self.assertGreater(segment.get_active_days(), 0)

    def test_existing_enable_date_is_kept(self):
        enabled = datetime(2026, 6, 1, tzinfo=timezone.utc)
        segment = self.make_segment(status=Segment.STATUS_ENABLED, enable_date=enabled)

        backfill_enable_date(apps, None)
        segment.refresh_from_db()

        self.assertEqual(segment.enable_date, enabled)

    def test_disabled_segment_is_left_alone(self):
        segment = self.make_segment(status=Segment.STATUS_DISABLED)

        backfill_enable_date(apps, None)
        segment.refresh_from_db()

        self.assertIsNone(segment.enable_date)
