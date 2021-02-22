from unittest.mock import patch

from captcha.client import RecaptchaResponse
from django.db import IntegrityError
from django.test import TestCase

from rca.enquire_to_study.factories import (
    EnquiryReasonFactory,
    FundingFactory,
    StartDateFactory,
)
from rca.enquire_to_study.forms import EnquireToStudyForm
from rca.enquire_to_study.models import (
    EnquiryFormSubmission,
    EnquiryFormSubmissionFundingsOrderable,
    EnquiryFormSubmissionProgrammesOrderable,
    EnquiryFormSubmissionProgrammeTypesOrderable,
)
from rca.programmes.factories import ProgrammePageFactory, ProgrammeTypeFactory


class TestEnquireToStudyForm(TestCase):
    def setUp(self):
        self.funding = FundingFactory()
        self.start_date = StartDateFactory()
        self.enquiry_reason = EnquiryReasonFactory()
        self.form_data = {
            "first_name": "Monty",
            "last_name": "python",
            "email": "person@form.com",
            "phone_number": "+12125552368",
            "country_of_residence": "GB",
            "city": "Bristol",
            "is_citizen": True,
            "programme_types": [ProgrammeTypeFactory().pk],
            "programmes": [ProgrammePageFactory(programme_type__pk=2).pk],
            "start_date": self.start_date.pk,
            "funding": [self.funding.pk],
            "enquiry_reason": self.enquiry_reason.pk,
            "is_read_data_protection_policy": True,
            "g-recaptcha-response": "PASSED",
        }

    def test_form_responds_to_path(self):
        response = self.client.get("/enquire-to-study/")
        self.assertEqual(response.status_code, 200)

    @patch("captcha.fields.client.submit")
    def test_valid_form(self, mocked_submit):
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)
        form = EnquireToStudyForm(data=self.form_data)
        form.is_valid()
        self.assertTrue(form.is_valid())

    @patch("captcha.fields.client.submit")
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
        self.assertEqual(self.form_data["is_citizen"], submission.is_citizen)
        # self.assertEqual(self.form_data["programme_types"], submission.programme_types)
        # self.assertEqual(self.form_data["programmes"], submission.programmes)
        self.assertEqual(self.start_date, submission.start_date)
        # self.assertEqual(self.form_data["funding"], submission.funding)
        self.assertEqual(self.enquiry_reason, submission.enquiry_reason)
        self.assertEqual(
            self.form_data["is_read_data_protection_policy"],
            submission.is_read_data_protection_policy,
        )

    @patch("captcha.fields.client.submit")
    def test_submissions_data(self, mocked_submit):
        # Test the submissions has programmes, programme_types and funding FKs
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)
        form = EnquireToStudyForm(data=self.form_data)
        form.is_valid()
        form.save()
        submission = EnquiryFormSubmission.objects.first()
        programme_types_orderable = (
            EnquiryFormSubmissionProgrammeTypesOrderable.objects.first()
        )
        programmes_orderable = EnquiryFormSubmissionProgrammesOrderable.objects.first()
        funding_orderable = EnquiryFormSubmissionFundingsOrderable.objects.first()

        self.assertEqual(programme_types_orderable.enquiry_submission, submission)
        self.assertEqual(programmes_orderable.enquiry_submission, submission)
        self.assertEqual(funding_orderable.enquiry_submission, submission)

        self.assertEqual(
            programme_types_orderable.programme_type.pk,
            self.form_data["programme_types"][0],
        )
        self.assertEqual(
            programmes_orderable.programme.pk, self.form_data["programmes"][0]
        )
        self.assertEqual(funding_orderable.funding.pk, self.form_data["funding"][0])

    @patch("captcha.fields.client.submit")
    def test_is_read_data_protection_policy_false(self, mocked_submit):
        # Test form errors with is_read_data_protection_policy false
        mocked_submit.return_value = RecaptchaResponse(is_valid=True)
        self.form_data["is_read_data_protection_policy"] = False
        form = EnquireToStudyForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertRaises(IntegrityError, form.save)

    # TODO
    # Test mailchimp
    # Test QS
