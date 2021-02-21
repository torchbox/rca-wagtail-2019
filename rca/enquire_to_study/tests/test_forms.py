from unittest.mock import patch

from captcha.client import RecaptchaResponse
from django.test import TestCase

from rca.enquire_to_study.factories import (
    EnquiryReasonFactory,
    FundingFactory,
    StartDateFactory,
)
from rca.enquire_to_study.forms import EnquireToStudyForm
from rca.enquire_to_study.models import EnquiryFormSubmission
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

        # TODO
        # Test the submissions has programmes, programme_types and funding FKs

    # TODO
    # Test form errors with is_read_data_protection_policy false
    # Test mailchimp
    # Test QS
