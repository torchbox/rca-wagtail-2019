from django.test import TestCase
from wagtail.test.utils import WagtailPageTestCase

from rca.home.models import HomePage
from rca.scholarships.factories import (
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


