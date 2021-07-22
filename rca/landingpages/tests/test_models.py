from django.test import TestCase
from wagtail.tests.utils import WagtailPageTests

from rca.home.models import HomePage
from rca.landingpages.factories import (
    EELandingPageFactory,
    EnterpriseLandingPageFactory,
    InnovationLandingPageFactory,
    LandingPageFactory,
    ResearchLandingPageFactory,
)
from rca.landingpages.models import EELandingPage


class TestLandingPageFactory(TestCase):
    def test_factories(self):
        EELandingPageFactory(),
        ResearchLandingPageFactory(),
        InnovationLandingPageFactory(),
        EnterpriseLandingPageFactory(),
        LandingPageFactory()


class TestEELandingPageRules(WagtailPageTests):
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
            )
        )
        # A second EELandingPage should not be creatable
        self.assertFalse(EELandingPage.can_create_at(self.home_page))
