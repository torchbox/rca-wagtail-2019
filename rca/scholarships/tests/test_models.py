from django.test import TestCase
from wagtail.tests.utils import WagtailPageTests

from rca.home.models import HomePage
from rca.scholarships.factories import (
    ScholarshipFactory,
    ScholarshipEnquiryFormSubmissionFactory,
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


class TestScholarshipsListingPageRules(WagtailPageTests):
    def setUp(self):
        self.home_page = HomePage.objects.first()

    def test_can_create(self):
        self.assertCanCreateAt(HomePage, ScholarshipsListingPage)

    def test_singlet(self):
        self.home_page.add_child(instance=ScholarshipsListingPage(title="Scholarships"))
        # A second ScholarshipsListingPage should not be creatable
        self.assertFalse(ScholarshipsListingPage.can_create_at(self.home_page))


class TestScholarshipFormFactory(TestCase):
    def test_factories(self):
        ScholarshipEnquiryFormSubmissionFactory()
