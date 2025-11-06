from django.test import TestCase
from wagtail.test.utils import WagtailPageTestCase

from rca.home.models import HomePage
from rca.landingpages.factories import (
    ALumniLandingPageFactory,
    DevelopmentLandingPageFactory,
    EELandingPageFactory,
    EnterpriseLandingPageFactory,
    InnovationLandingPageFactory,
    LandingPageFactory,
    ResearchLandingPageFactory,
)
from rca.landingpages.models import (
    AlumniLandingPage,
    DevelopmentLandingPage,
    EELandingPage,
)


class TestLandingPageFactory(TestCase):
    def test_factories(self):
        EELandingPageFactory(),
        ResearchLandingPageFactory(),
        InnovationLandingPageFactory(),
        EnterpriseLandingPageFactory(),
        LandingPageFactory(),
        ALumniLandingPageFactory(),
        DevelopmentLandingPageFactory()


class TestEELandingPageRules(WagtailPageTestCase):
    def setUp(self):
        self.home_page = HomePage.objects.first()

    def test_can_create(self):
        self.assertCanCreateAt(HomePage, EELandingPage)

    def test_singlet(self):
        self.home_page.add_child(
            instance=EELandingPage(
                title="EE Landing Page",
                news_link_text="View more",
                news_link_target_url="https://rca.ac.uk",
                events_link_text="View more",
                events_link_target_url="https://rca.ac.uk",
                stories_link_text="View more",
                stories_link_target_url="https://rca.ac.uk",
                stories_summary_text="These are the stories",
                podcasts_link_text="View more",
                podcasts_link_target_url="https://rca.ac.uk",
                podcasts_summary_text="These are the talks",
                cta_navigation_title="Media centre",
            )
        )
        # A second EELandingPage should not be creatable
        self.assertFalse(EELandingPage.can_create_at(self.home_page))


class TestAlumniLandingPageRules(WagtailPageTestCase):
    def setUp(self):
        self.home_page = HomePage.objects.first()

    def test_can_create(self):
        self.assertCanCreateAt(HomePage, AlumniLandingPage)

    def test_singlet(self):
        self.home_page.add_child(
            instance=AlumniLandingPage(
                title="Alumni Landing Page",
                news_link_text="News",
                news_link_target_url="https://rca.ac.uk/news",
            )
        )
        # A second AlumniLandingPage should not be creatable
        self.assertFalse(AlumniLandingPage.can_create_at(self.home_page))


class TestDevelopmentLandingPageRules(WagtailPageTestCase):
    def setUp(self):
        self.home_page = HomePage.objects.first()

    def test_can_create(self):
        self.assertCanCreateAt(HomePage, DevelopmentLandingPage)

    def test_singlet(self):
        self.home_page.add_child(
            instance=DevelopmentLandingPage(
                title="Development Landing Page",
                stories_link_text="View more",
                stories_link_target_url="https://rca.ac.uk",
            )
        )
        # A second DevelopmentLandingPage should not be creatable
        self.assertFalse(DevelopmentLandingPage.can_create_at(self.home_page))
