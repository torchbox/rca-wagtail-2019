from datetime import timedelta
from http import HTTPStatus
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django_recaptcha.client import RecaptchaResponse
from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from rca.enquire_to_study.factories import (
    EnquiryFormSubmissionFactory,
    EnquiryReasonFactory,
    StartDateFactory,
)
from rca.enquire_to_study.forms import EnquireToStudyForm
from rca.enquire_to_study.models import EnquireToStudySettings, EnquiryFormSubmission
from rca.enquire_to_study.views import EnquireToStudyFormView
from rca.enquire_to_study.wagtail_hooks import EnquiryFormSubmissionAdmin
from rca.programmes.factories import (
    ProgrammePageFactory,
    ProgrammePageProgrammeTypeFactory,
    ProgrammeTypeFactory,
)


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


@override_settings(
    RCA_DNR_EMAIL="test@example.com",
    ENQUIRE_TO_STUDY_DESTINATION_EMAILS=["test2@example.com"],
)
class EnquireToStudyFormViewInternalEmailsTest(WagtailPageTestCase):
    def setUp(self):
        EnquireToStudySettings.objects.create(
            # Set to `False` since these tests are not testing `send_user_email_notification`.
            email_submission_notifations=False,
            email_subject="Test email subject",
            email_content="Test email content",
            site_id=Site.objects.get().pk,
        )
        page = ProgrammePageFactory(qs_code=1)
        ProgrammePageProgrammeTypeFactory(
            page=page, programme_type=ProgrammeTypeFactory()
        )

        self.form_data = {
            "first_name": "Monty",
            "last_name": "Python",
            "email": "monthpython@holygrail.com",
            "phone_number": "+12125552368",
            "country_of_residence": "GB",
            "city": "Bristol",
            "country_of_citizenship": "GB",
            "programmes": [page.pk],
            "start_date": StartDateFactory(qs_code="test-code").pk,
            "enquiry_reason": EnquiryReasonFactory().pk,
            "enquiry_questions": "What is your name?",
            "is_read_data_protection_policy": True,
            "g-recaptcha-response": "PASSED",
        }

        request = RequestFactory().get(
            reverse("enquire_to_study:enquire_to_study_form")
        )
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()
        self.view = EnquireToStudyFormView()
        self.view.setup(request)

    @patch("django_recaptcha.fields.client.submit")
    def test_email_is_sent_internally_when_gb_or_ie_and_has_questions(
        self, mocked_submit
    ):
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)

        form = EnquireToStudyForm(data=self.form_data)
        form.is_valid()
        self.view.form_valid(form)
        submission = EnquiryFormSubmission.objects.last()

        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]

        self.assertIn(f"Submission ID: {str(submission.id)}", email.body)
        self.assertIn(f"First name: {self.form_data['first_name']}", email.body)
        self.assertIn(f"Last name: {self.form_data['last_name']}", email.body)
        self.assertEqual(["test2@example.com"], email.to)

    @patch("django_recaptcha.fields.client.submit")
    def test_email_is_not_sent_internally_if_not_in_gb_or_ie(self, mocked_submit):
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)

        self.form_data["country_of_residence"] = "PH"

        # Make sure that this is still set.
        self.assertEqual(self.form_data["enquiry_questions"], "What is your name?")

        form = EnquireToStudyForm(data=self.form_data)
        form.is_valid()
        self.view.form_valid(form)
        self.assertEqual(0, len(mail.outbox))

    @patch("django_recaptcha.fields.client.submit")
    def test_email_is_not_sent_if_no_enquiry_questions(self, mocked_submit):
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)

        self.form_data["enquiry_questions"] = ""

        # Make sure that this is still `GB`.
        self.assertEqual(self.form_data["country_of_citizenship"], "GB")

        form = EnquireToStudyForm(data=self.form_data)
        form.is_valid()
        self.view.form_valid(form)
        self.assertEqual(0, len(mail.outbox))


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
        self.submission__1 = EnquiryFormSubmissionFactory()
        self.submission_2 = EnquiryFormSubmissionFactory()
        self.submission_3 = EnquiryFormSubmissionFactory()
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
