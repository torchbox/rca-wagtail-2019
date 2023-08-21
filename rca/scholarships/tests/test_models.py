from django.test import TestCase
from wagtail.test.utils import WagtailPageTestCase

from rca.home.models import HomePage
from rca.scholarships.factories import (
    ScholarshipEnquiryFormSubmissionFactory,
    ScholarshipFactory,
    ScholarshipFeeStatusFactory,
    ScholarshipFundingFactory,
    ScholarshipLocationFactory,
    ScholarshipsListingPageFactory,
)
from rca.scholarships.models import ScholarshipsListingPage


class TestScholarshipFactory(TestCase):
    def test_factories(self):
        ScholarshipFactory()


class TestScholarshipsTaxonomyFactory(TestCase):
    def test_factories(self):
        ScholarshipFeeStatusFactory()
        ScholarshipFundingFactory()
        ScholarshipLocationFactory()


class TestScholarshipsListingPageFactory(TestCase):
    def test_factories(self):
        ScholarshipsListingPageFactory()


class TestScholarshipsListingPageRules(WagtailPageTestCase):
    def test_can_create(self):
        self.assertCanCreateAt(HomePage, ScholarshipsListingPage)

    def test_singlet(self):
        home_page = HomePage.objects.first()
        ScholarshipsListingPageFactory(parent=home_page)
        # A second ScholarshipsListingPage should not be creatable
        self.assertFalse(ScholarshipsListingPage.can_create_at(home_page))


class TestScholarshipFormFactory(TestCase):
    def test_factories(self):
        ScholarshipEnquiryFormSubmissionFactory()


class TestScholarshipEnquiryFormSubmission(TestCase):
    def test_get_scholarships(self):
        scholarship1 = ScholarshipFactory()
        scholarship2 = ScholarshipFactory()
        submission = ScholarshipEnquiryFormSubmissionFactory(
            scholarships=[scholarship1, scholarship2]
        )

        scholarships = submission.get_scholarships()

        self.assertEqual(2, len(scholarships))
        self.assertEqual(scholarships[0].id, scholarship1.id)
        self.assertEqual(scholarships[1].id, scholarship2.id)
