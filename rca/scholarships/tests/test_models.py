from django.test import TestCase

from wagtail.test.utils import WagtailPageTestCase

from rca.home.models import HomePage
from rca.programmes.factories import ProgrammePageFactory
from rca.programmes.models import ProgrammePage
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


class TestScholarshipsListingPageGetContextProgramme(WagtailPageTestCase):
    def setUp(self):
        self.home_page = HomePage.objects.first()
        self.listing_page = ScholarshipsListingPageFactory(parent=self.home_page)

    def test_no_programme_param_leaves_programme_none(self):
        response = self.client.get(self.listing_page.url)
        self.assertIsNone(response.context["programme"])

    def test_unknown_programme_slug_leaves_programme_none(self):
        response = self.client.get(
            self.listing_page.url, {"programme": "does-not-exist"}
        )
        self.assertIsNone(response.context["programme"])

    def test_duplicate_programme_slug_leaves_programme_none(self):
        first = ProgrammePageFactory(parent=self.home_page, slug="first-programme")
        second = ProgrammePageFactory(parent=self.home_page, slug="second-programme")
        # Simulates a data-integrity issue (e.g. a bad migration) giving two
        # live pages the same slug, bypassing Wagtail's usual uniqueness check
        # on save().
        ProgrammePage.objects.filter(pk=second.pk).update(slug=first.slug)

        response = self.client.get(self.listing_page.url, {"programme": first.slug})
        self.assertIsNone(response.context["programme"])
