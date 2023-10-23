from datetime import timedelta
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rca.scholarships.factories import ScholarshipEnquiryFormSubmissionFactory
from rca.scholarships.models import ScholarshipEnquiryFormSubmission
from rca.scholarships.wagtail_hooks import ScholarshipEnquiryFormSubmissionAdmin


class ScholarshipEnquireToStudyFormDeleteViewTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = get_user_model().objects.create_user(
            username="test",
            email="test@email.com",
            password="password",
            is_superuser=True,
        )
        self.user.user_permissions.add(
            Permission.objects.get(codename="access_admin"),
            Permission.objects.get(codename="add_site"),
            Permission.objects.get(codename="change_site"),
            Permission.objects.get(codename="delete_site"),
        )
        self.denied_user = get_user_model().objects.create_user(
            username="denied",
            email="denied@email.com",
            password="password",
            is_superuser=False,
        )

        # Add submissions
        self.submission__1 = ScholarshipEnquiryFormSubmissionFactory()
        self.submission_2 = ScholarshipEnquiryFormSubmissionFactory()
        self.submission_3 = ScholarshipEnquiryFormSubmissionFactory()
        today = timezone.now()
        seven_days_ago = today - timedelta(days=7)
        self.submission_3.submission_date = seven_days_ago
        self.submission_3.save()

    def test_non_superuser_is_redirected(self):
        self.client.login(username="denied", password="password")
        response = self.client.get(reverse("scholarships_delete"))
        self.assertEqual(response.status_code, 302)

    def test_path_existed(self):
        self.client.login(username="test", password="password")

        response = self.client.get(reverse("scholarships_delete"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        submissions_count = ScholarshipEnquiryFormSubmission.objects.count()
        self.assertEqual(submissions_count, 3)

    def test_submissions_older_than_seven_days_are_deleted(self):
        self.client.login(username="test", password="password")

        url_helper = ScholarshipEnquiryFormSubmissionAdmin().url_helper
        index_url = url_helper.get_action_url("index")

        response = self.client.post(reverse("scholarships_delete"), follow=True)
        self.assertRedirects(response, index_url, status_code=302)

        submissions_count = ScholarshipEnquiryFormSubmission.objects.count()
        self.assertEqual(submissions_count, 2)
