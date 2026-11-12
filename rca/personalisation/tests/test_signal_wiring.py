from django.test import TestCase
from wagtail_personalisation.models import Segment

from rca.personalisation.factories import SegmentFactory


class SegmentStatusSignalTest(TestCase):
    """
    wagtail_personalisation.config.WagtailPersonalisationConfig.ready()
    connects a pre_save receiver on Segment that stamps enable_date /
    disable_date whenever status changes. That receiver only runs if
    INSTALLED_APPS points at the real AppConfig rather than the bare
    "wagtail_personalisation" app name - a regression here would silently
    leave every segment showing "active for 0 days" in the admin dashboard.
    """

    def test_enabling_a_segment_sets_enable_date_and_resets_visit_count(self):
        segment = SegmentFactory(
            status=Segment.STATUS_DISABLED, visit_count=5, enable_date=None
        )

        segment.status = Segment.STATUS_ENABLED
        segment.save()
        segment.refresh_from_db()

        self.assertIsNotNone(segment.enable_date)
        self.assertEqual(segment.visit_count, 0)

    def test_disabling_a_segment_sets_disable_date(self):
        segment = SegmentFactory(status=Segment.STATUS_ENABLED)

        segment.status = Segment.STATUS_DISABLED
        segment.save()
        segment.refresh_from_db()

        self.assertIsNotNone(segment.disable_date)
