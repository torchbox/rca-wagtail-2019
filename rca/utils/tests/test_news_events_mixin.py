import datetime
from datetime import date

import wagtail_factories
from django.test import override_settings
from faker import Faker
from wagtail.images.tests.utils import Image, get_test_image_file
from wagtail.test.utils import WagtailPageTestCase

from rca.editorial.models import (
    EditorialPage,
    EditorialPageTypePlacement,
    EditorialType,
)
from rca.events.factories import EventEligibilityFactory, EventLocationFactory
from rca.events.models import EventDetailPage, EventDetailPageEventType, EventType
from rca.home.models import HomePage
from rca.landingpages.models import RelatedLandingPage, ResearchLandingPage
from rca.research.models import RelatedResearchCenterPage, ResearchCentrePage
from rca.schools.models import RelatedSchoolPage, SchoolPage

fake = Faker()


def date_helper():
    future_date = fake.date_between(start_date="now", end_date="+1y")
    return {
        "start_date": future_date,
        "end_date": future_date + datetime.timedelta(days=3),
    }


@override_settings(USE_TZ=False)
class NewsAndEventsMixinTest(WagtailPageTestCase):
    """
    There is a lot of page setup and handwaving here, however the main aim
    of these tests are to ensure data from internal relationships is being
    returned. Should the relationships change, or someone removes LegacyNewsAndEventsMixin
    (which is planned) we want these to fail.
    """

    def setUp(self):
        self.editorial_type = EditorialType(title="Art")
        self.editorial_type.save()
        self.event_type = EventType(title="Exhibition")
        self.event_type.save()

        # make 3 event pages related to the above
        self.image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(colour="white"),
        )
        self.home_page = HomePage.objects.first()

        # Create pages to test
        self.school_page = SchoolPage(
            title=fake.words(3),
            introduction="Introduction",
            body="body",
            introduction_image=wagtail_factories.ImageFactory(title="test image"),
        )
        self.home_page.add_child(instance=self.school_page)

        self.research_centre_page = ResearchCentrePage(
            title=fake.words(3), related_programmes_title="Related_programms"
        )
        self.home_page.add_child(instance=self.research_centre_page)

        self.landing_page = ResearchLandingPage(
            title=fake.words(3),
        )
        self.home_page.add_child(instance=self.landing_page)

        # Make EditorialPages we expecting to be returned
        self.editorial_page = EditorialPage(
            title="The editorial page",
            published_at=date(2021, 1, 4),
            introduction=fake.sentence(),
            hero_image=wagtail_factories.ImageFactory(),
            editorial_types=[EditorialPageTypePlacement(type=self.editorial_type)],
            related_schools=[RelatedSchoolPage(page=self.school_page)],
            related_research_centre_pages=[
                RelatedResearchCenterPage(page=self.research_centre_page)
            ],
            related_landing_pages=[RelatedLandingPage(page=self.landing_page)],
        )
        self.home_page.add_child(instance=self.editorial_page)

        # Make EventDetailPages we expecting to be returned
        dates = date_helper()
        self.event_detail_page = EventDetailPage(
            title="The event page",
            introduction=fake.sentence(),
            hero_image=wagtail_factories.ImageFactory(),
            start_date=dates["start_date"],
            end_date=dates["end_date"],
            related_schools=[RelatedSchoolPage(page=self.school_page)],
            related_research_centre_pages=[
                RelatedResearchCenterPage(page=self.research_centre_page)
            ],
            related_landing_pages=[RelatedLandingPage(page=self.landing_page)],
            location=EventLocationFactory(),
            eligibility=EventEligibilityFactory(),
        )
        self.home_page.add_child(instance=self.event_detail_page)
        EventDetailPageEventType.objects.create(
            source_page=self.event_detail_page,
            event_type=self.event_type,
        )

    def test_schools_page_related_editorial(self):
        self.assertIn(
            "fill-878x472.jpg", self.school_page.legacy_news_and_events[0]["image"]
        )
        self.assertEqual(
            self.school_page.legacy_news_and_events[0]["title"], "The editorial page"
        )
        self.assertEqual(
            self.school_page.legacy_news_and_events[0]["description"], "4 January 2021"
        )
        self.assertEqual(
            self.school_page.legacy_news_and_events[0]["link"], "/the-editorial-page/"
        )
        self.assertEqual(
            self.school_page.legacy_news_and_events[0]["type"].title, "Art"
        )

    def test_school_page_related_event(self):
        self.assertIn(
            "fill-878x472.jpg", self.school_page.legacy_news_and_events[1]["image"]
        )
        self.assertEqual(
            self.school_page.legacy_news_and_events[1]["title"], "The event page"
        )
        self.assertEqual(
            self.school_page.legacy_news_and_events[1]["description"],
            self.event_detail_page.event_date_short,
        )
        self.assertEqual(
            self.school_page.legacy_news_and_events[1]["link"], "/the-event-page/"
        )
        self.assertEqual(self.school_page.legacy_news_and_events[1]["type"], "Event")

    def test_research_page_related_editorial(self):
        self.assertIn(
            "fill-878x472.jpg",
            self.research_centre_page.legacy_news_and_events[0]["image"],
        )
        self.assertEqual(
            self.research_centre_page.legacy_news_and_events[0]["title"],
            "The editorial page",
        )
        self.assertEqual(
            self.research_centre_page.legacy_news_and_events[0]["description"],
            "4 January 2021",
        )
        self.assertEqual(
            self.research_centre_page.legacy_news_and_events[0]["link"],
            "/the-editorial-page/",
        )
        self.assertEqual(
            self.research_centre_page.legacy_news_and_events[0]["type"].title, "Art"
        )

    def test_research_page_related_event(self):
        self.assertIn(
            "fill-878x472.jpg",
            self.research_centre_page.legacy_news_and_events[1]["image"],
        )
        self.assertEqual(
            self.research_centre_page.legacy_news_and_events[1]["title"],
            "The event page",
        )
        self.assertEqual(
            self.research_centre_page.legacy_news_and_events[1]["description"],
            self.event_detail_page.event_date_short,
        )
        self.assertEqual(
            self.research_centre_page.legacy_news_and_events[1]["link"],
            "/the-event-page/",
        )
        self.assertEqual(
            self.research_centre_page.legacy_news_and_events[1]["type"], "Event"
        )

    def test_landing_page_related_editorial(self):
        self.assertIn(
            "fill-878x472.jpg", self.landing_page.legacy_news_and_events[0]["image"]
        )
        self.assertEqual(
            self.landing_page.legacy_news_and_events[0]["title"], "The editorial page"
        )
        self.assertEqual(
            self.landing_page.legacy_news_and_events[0]["description"], "4 January 2021"
        )
        self.assertEqual(
            self.landing_page.legacy_news_and_events[0]["link"], "/the-editorial-page/"
        )
        self.assertEqual(
            self.landing_page.legacy_news_and_events[0]["type"].title, "Art"
        )

    def test_landing_page_related_event(self):
        self.assertIn(
            "fill-878x472.jpg", self.landing_page.legacy_news_and_events[1]["image"]
        )
        self.assertEqual(
            self.landing_page.legacy_news_and_events[1]["title"], "The event page"
        )
        self.assertEqual(
            self.landing_page.legacy_news_and_events[1]["description"],
            self.event_detail_page.event_date_short,
        )
        self.assertEqual(
            self.landing_page.legacy_news_and_events[1]["link"], "/the-event-page/"
        )
        self.assertEqual(self.landing_page.legacy_news_and_events[1]["type"], "Event")
