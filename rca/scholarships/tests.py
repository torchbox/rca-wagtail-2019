from django.test import TestCase
from wagtail.tests.utils import WagtailPageTests

from rca.home.models import HomePage
from rca.scholarships.factories import ScholarshipsListingPageFactory
from rca.scholarships.models import ScholarshipsListingPage


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
