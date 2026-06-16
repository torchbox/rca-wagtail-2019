from django.test import TestCase
from django.urls import reverse
from wagtail.test.utils import WagtailTestUtils

from rca.enquire_to_study.factories import EnquiryFormSubmissionFactory
from rca.enquire_to_study.models import (
    EnquiryFormSubmission,
    EnquiryFormSubmissionProgrammesOrderable,
)
from rca.programmes.factories import ProgrammePageFactory


class EnquiryFormSubmissionViewSetTest(WagtailTestUtils, TestCase):
    def setUp(self):
        self.user = self.login()
        self.index_url = reverse("enquiryformsubmission:index")

    def test_index_loads(self):
        EnquiryFormSubmissionFactory()
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)

    def test_create_disabled_for_all_users(self):
        # The add view is gated behind the "add" permission, which the custom
        # policy denies for everyone (including this superuser).
        response = self.client.get(reverse("enquiryformsubmission:add"))
        self.assertNotEqual(response.status_code, 200)

    def test_add_button_not_rendered(self):
        response = self.client.get(self.index_url)
        self.assertNotContains(response, reverse("enquiryformsubmission:add"))

    def test_programmes_column_rendered(self):
        submission = EnquiryFormSubmissionFactory(first_name="Columncheck")
        page = ProgrammePageFactory(title="MA Curating")
        EnquiryFormSubmissionProgrammesOrderable.objects.create(
            enquiry_submission=submission, programme=page
        )
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "MA Curating")

    def test_programme_filter_is_dropdown(self):
        ProgrammePageFactory(title="MA Curating")
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        # The relation filter must render as a <select> dropdown, not a text input.
        self.assertContains(response, '<select name="programme"')

    def test_submission_date_range_filter(self):
        from datetime import timedelta

        from django.utils import timezone

        EnquiryFormSubmissionFactory(first_name="RecentPerson")
        old = EnquiryFormSubmissionFactory(first_name="OldPerson")
        # submission_date is auto_now_add; override after creation.
        EnquiryFormSubmission.objects.filter(pk=old.pk).update(
            submission_date=timezone.now() - timedelta(days=30)
        )
        cutoff = (timezone.now() - timedelta(days=7)).date().isoformat()
        response = self.client.get(self.index_url, {"submission_date_from": cutoff})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "RecentPerson")
        self.assertNotContains(response, "OldPerson")

    def test_search(self):
        EnquiryFormSubmissionFactory(first_name="Findme", last_name="Searchable")
        EnquiryFormSubmissionFactory(first_name="Hidden", last_name="Nope")
        response = self.client.get(self.index_url, {"q": "Findme"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Findme")
        self.assertNotContains(response, "Hidden")

    def test_export_contains_all_columns(self):
        submission = EnquiryFormSubmissionFactory(first_name="Exportme")
        page = ProgrammePageFactory(title="MA Exporting")
        EnquiryFormSubmissionProgrammesOrderable.objects.create(
            enquiry_submission=submission, programme=page
        )
        response = self.client.get(self.index_url, {"export": "csv"})
        self.assertEqual(response.status_code, 200)
        content = b"".join(response.streaming_content).decode()
        # Custom callable column headings and data appear in the export.
        self.assertIn("Programmes", content)
        self.assertIn("Country of residence", content)
        self.assertIn("Exportme", content)
        self.assertIn("MA Exporting", content)

    def test_delete_header_button_links_to_custom_view(self):
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("enquiretostudy_delete"))

    def test_menu_label_and_placement(self):
        from rca.enquire_to_study.viewsets import EnquiryFormSubmissionViewSet

        viewset = EnquiryFormSubmissionViewSet()
        self.assertEqual(viewset.menu_label, "Enquiry Submissions")
        self.assertEqual(viewset.menu_order, 200)
        self.assertTrue(viewset.add_to_admin_menu)
        self.assertFalse(viewset.add_to_settings_menu)
