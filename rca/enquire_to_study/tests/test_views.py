from datetime import timedelta
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from rca.enquire_to_study.factories import (
    EnquiryFormSubmissionFactory,
    EnquiryReasonFactory,
    StartDateFactory,
)
from rca.enquire_to_study.models import EnquiryFormSubmission
from rca.enquire_to_study.views import EnquireToStudyFormView
from rca.enquire_to_study.wagtail_hooks import EnquiryFormSubmissionAdmin


class EnquireToStudyFormViewTest(TestCase):
    def test_path_existed(self):
        response = self.client.get(reverse("enquire_to_study:enquire_to_study_form"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_environment_set_in_context(self):
        request = RequestFactory().get(
            reverse("enquire_to_study:enquire_to_study_form")
        )
        view = EnquireToStudyFormView()
        view.setup(request)

        context = view.get_context_data()
        self.assertIn("form", context)


class EnquireToStudyFormThanksViewTest(TestCase):
    def test_path_existed(self):
        response = self.client.get(reverse("enquire_to_study:enquire_to_study_thanks"))
        self.assertEqual(response.status_code, HTTPStatus.OK)


class EnquireToStudyFormDeleteViewTest(TestCase):
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

        # Add submissions
        self.enquiry_reason = EnquiryReasonFactory()
        self.start_date = StartDateFactory()
        self.submission__1 = EnquiryFormSubmissionFactory(
            enquiry_reason=self.enquiry_reason, start_date=self.start_date
        )
        self.submission_2 = EnquiryFormSubmissionFactory(
            enquiry_reason=self.enquiry_reason, start_date=self.start_date,
        )
        self.submission_3 = EnquiryFormSubmissionFactory(
            enquiry_reason=self.enquiry_reason, start_date=self.start_date,
        )
        today = timezone.now()
        seven_days_ago = today - timedelta(days=7)
        self.submission_3.submission_date = seven_days_ago
        self.submission_3.save()

    def test_path_existed(self):
        self.client.login(username="test", password="password")

        response = self.client.get(reverse("enquiretostudy_delete"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        submissions_count = EnquiryFormSubmission.objects.count()
        self.assertEqual(submissions_count, 3)

    def test_submissions_older_than_seven_days_are_deleted(self):
        self.client.login(username="test", password="password")

        url_helper = EnquiryFormSubmissionAdmin().url_helper
        index_url = url_helper.get_action_url("index")

        response = self.client.post(reverse("enquiretostudy_delete"), follow=True)
        self.assertRedirects(response, index_url, status_code=302)

        submissions_count = EnquiryFormSubmission.objects.count()
        self.assertEqual(submissions_count, 2)
