from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase
from django_recaptcha.client import RecaptchaResponse

from rca.enquire_to_study.factories import EnquiryReasonFactory, StartDateFactory
from rca.enquire_to_study.forms import EnquireToStudyForm
from rca.enquire_to_study.models import (
    EnquiryFormSubmission,
    EnquiryFormSubmissionProgrammesOrderable,
)
from rca.programmes.factories import (
    ProgrammePageFactory,
    ProgrammePageProgrammeTypeFactory,
    ProgrammeTypeFactory,
)


class TestEnquireToStudyForm(TestCase):
    def setUp(self):
        self.start_date = StartDateFactory(qs_code="test-code")
        self.enquiry_reason = EnquiryReasonFactory()
        page = ProgrammePageFactory(qs_code=1)
        ProgrammePageProgrammeTypeFactory(
            page=page, programme_type=ProgrammeTypeFactory()
        )
        self.form_data = {
            "first_name": "Monty",
            "last_name": "python",
            "email": "monthpython@holygrail.com",
            "phone_number": "+12125552368",
            "country_of_residence": "GB",
            "city": "Bristol",
            "country_of_citizenship": "GB",
            "programmes": [page.pk],
            "start_date": self.start_date.pk,
            "enquiry_reason": self.enquiry_reason.pk,
            "enquiry_questions": "What is your name?",
            "is_read_data_protection_policy": True,
            "g-recaptcha-response": "PASSED",
        }

    def test_form_responds_to_path(self):
        response = self.client.get("/register-your-interest/")
        self.assertEqual(response.status_code, 200)

    @patch("django_recaptcha.fields.client.submit")
    def test_valid_form(self, mocked_submit):
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)
        form = EnquireToStudyForm(data=self.form_data)
        form.is_valid()
        self.assertTrue(form.is_valid())

    @patch("django_recaptcha.fields.client.submit")
    def test_form_save(self, mocked_submit):
        # Test form save creates submission
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)
        form = EnquireToStudyForm(data=self.form_data)
        form.is_valid()
        form.save()
        submission = EnquiryFormSubmission.objects.first()
        self.assertEqual(self.form_data["first_name"], submission.first_name)
        self.assertEqual(self.form_data["last_name"], submission.last_name)
        self.assertEqual(self.form_data["email"], submission.email)
        self.assertEqual(self.form_data["phone_number"], submission.phone_number)
        self.assertEqual(
            self.form_data["country_of_residence"], submission.country_of_residence
        )
        self.assertEqual(self.form_data["city"], submission.city)
        self.assertEqual(
            self.form_data["programmes"][0],
            submission.enquiry_submission_programmes.first().programme.id,
        )
        self.assertEqual(self.start_date, submission.start_date)
        self.assertEqual(self.enquiry_reason, submission.enquiry_reason)
        self.assertEqual(
            self.form_data["is_read_data_protection_policy"],
            submission.is_read_data_protection_policy,
        )

    @patch("django_recaptcha.fields.client.submit")
    def test_submissions_data(self, mocked_submit):
        # Test the submission created has programmes
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)
        form = EnquireToStudyForm(data=self.form_data)
        form.is_valid()
        form.save()
        submission = EnquiryFormSubmission.objects.first()
        programmes_orderable = EnquiryFormSubmissionProgrammesOrderable.objects.first()

        self.assertEqual(programmes_orderable.enquiry_submission, submission)
        self.assertEqual(
            programmes_orderable.programme.pk, self.form_data["programmes"][0]
        )

    @patch("django_recaptcha.fields.client.submit")
    def test_is_read_data_protection_policy_false(self, mocked_submit):
        # Test form errors with is_read_data_protection_policy false
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)
        self.form_data["is_read_data_protection_policy"] = False
        form = EnquireToStudyForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertRaises(IntegrityError, form.save)
