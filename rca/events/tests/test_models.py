from datetime import date, time

import wagtail_factories
from django.core.exceptions import ValidationError
from django.test import TestCase
from freezegun import freeze_time
from wagtail.test.utils import WagtailPageTestCase

from rca.editorial.factories import EditorialPageFactory, EditorialTypeFactory
from rca.editorial.models import EditorialPageTypePlacement
from rca.events.factories import (
    EventAvailabilityFactory,
    EventDetailPageFactory,
    EventEligibility,
    EventEligibilityFactory,
    EventLocationFactory,
    EventSeriesFactory,
)
from rca.events.models import (
    EventDetailPage,
    EventDetailPageRelatedPages,
    EventIndexPage,
)
from rca.guides.factories import GuidePageFactory
from rca.home.models import HomePage
from rca.landingpages.factories import (
    EELandingPageFactory,
    EnterpriseLandingPageFactory,
    InnovationLandingPageFactory,
    ResearchLandingPageFactory,
)
from rca.programmes.factories import ProgrammePageFactory
from rca.research.factories import ResearchCentrePageFactory
from rca.schools.factories import SchoolPageFactory
from rca.shortcourses.factories import ShortCoursePageFactory
from rca.standardpages.models import IndexPage, InformationPage


class TestEventDetailPageFactories(TestCase):
    def test_factories(self):
        EventDetailPageFactory()
        EventLocationFactory()
        EventAvailabilityFactory()
        EventEligibility()


class EventDetailPageTests(WagtailPageTestCase):
    def test_can_create_under_event_index_page(self):
        self.assertCanCreateAt(EventIndexPage, EventDetailPage)

    def test_cant_create_under_other_pages(self):
        self.assertCanNotCreateAt(IndexPage, EventDetailPage)
        self.assertCanNotCreateAt(InformationPage, EventDetailPage)
        self.assertCanNotCreateAt(HomePage, EventDetailPage)

    @freeze_time("2021-01-03")
    def test_get_series_events(self):
        home_page = HomePage.objects.first()
        series = EventSeriesFactory()
        event1 = EventDetailPageFactory(
            parent=home_page,
            start_date=date(2021, 1, 4),
            end_date=date(2021, 1, 5),
            series=series,
        )
        event2 = EventDetailPageFactory(
            parent=home_page,
            start_date=date(2021, 1, 6),
            end_date=date(2021, 1, 7),
            series=series,
        )
        event3 = EventDetailPageFactory(
            parent=home_page,
            start_date=date(2021, 1, 8),
            end_date=date(2021, 1, 9),
            series=series,
        )
        event4 = EventDetailPageFactory(
            parent=home_page,
            start_date=date(2021, 1, 1),
            end_date=date(2021, 1, 2),
            series=series,
        )
        # different series, should not show
        EventDetailPageFactory(
            parent=home_page,
            start_date=date(2021, 1, 6),
            end_date=date(2021, 1, 7),
            series=EventSeriesFactory(),
        )
        self.assertEqual(
            [
                {
                    "title": event2.title,
                    "link": event2.url,
                    "meta": "",
                    "description": event2.introduction,
                    "image": None,
                },
                {
                    "title": event3.title,
                    "link": event3.url,
                    "meta": "",
                    "description": event3.introduction,
                    "image": None,
                },
                {
                    "title": event4.title,
                    "link": event4.url,
                    "meta": "",
                    "description": event4.introduction,
                    "image": None,
                },
            ],
            event1.get_series_events(),
        )


class EventDetailPageDateTests(WagtailPageTestCase):
    """
    Tests for the return values of the event_date_short method
    """

    def setUp(self):
        self.home_page = HomePage.objects.first()

    def test_one_day_event(self):
        one_day_event = EventDetailPageFactory(
            parent=self.home_page,
            start_date=date(2021, 1, 6),
            end_date=date(2021, 1, 6),
            series=EventSeriesFactory(),
            location=EventLocationFactory(),
            eligibility=EventEligibilityFactory(),
        )
        self.assertEqual(one_day_event.event_date_short, "6 January 2021")

    def test_same_month_event(self):
        same_month_event = EventDetailPageFactory(
            parent=self.home_page,
            start_date=date(2021, 1, 6),
            end_date=date(2021, 1, 9),
            series=EventSeriesFactory(),
            location=EventLocationFactory(),
            eligibility=EventEligibilityFactory(),
        )
        self.assertEqual(same_month_event.event_date_short, "6 - 9 January 2021")

    def test_different_month_event(self):
        different_month_event = EventDetailPageFactory(
            parent=self.home_page,
            start_date=date(2021, 1, 6),
            end_date=date(2021, 2, 9),
            series=EventSeriesFactory(),
            location=EventLocationFactory(),
            eligibility=EventEligibilityFactory(),
        )
        self.assertEqual(
            different_month_event.event_date_short, "6 January - 9 February 2021"
        )

    def test_different_year_event(self):
        different_year_event = EventDetailPageFactory(
            parent=self.home_page,
            start_date=date(2021, 12, 29),
            end_date=date(2022, 1, 1),
            series=EventSeriesFactory(),
            location=EventLocationFactory(),
            eligibility=EventEligibilityFactory(),
        )
        self.assertEqual(
            different_year_event.event_date_short, "29 December 2021 - 1 January 2022"
        )

    def test_past_event(self):
        event = EventDetailPageFactory.build(
            parent=self.home_page,
            start_date=date(2021, 12, 29),
            end_date=date(2022, 1, 1),
            location=EventLocationFactory(),
            eligibility=EventEligibilityFactory(),
        )
        self.assertTrue(event.past)

    def test_future_event(self):
        event = EventDetailPageFactory.build(
            parent=self.home_page,
            start_date=date(2091, 12, 29),
            end_date=date(2092, 1, 1),
            location=EventLocationFactory(),
            eligibility=EventEligibilityFactory(),
        )
        self.assertFalse(event.past)

    def test_event_time(self):
        testcases = (
            ("", EventDetailPageFactory.build(start_time=None, end_time=None)),
            (
                "9am – 5:30pm",
                EventDetailPageFactory.build(start_time=time(9), end_time=time(17, 30)),
            ),
            (
                "9:30am – 5pm",
                EventDetailPageFactory.build(start_time=time(9, 30), end_time=time(17)),
            ),
            (
                "12pm – 11:59pm",
                EventDetailPageFactory.build(
                    start_time=time(12), end_time=time(23, 59)
                ),
            ),
            (
                "12am – 11:59am",
                EventDetailPageFactory.build(
                    start_time=time(00), end_time=time(11, 59)
                ),
            ),
        )
        for test, page in testcases:
            with self.subTest(f"Testing time format: {test}", test=test, page=page):
                self.assertEqual(test, page.event_time)

    def test_event_time_validation(self):
        testcases = (
            (time(17, 30), time(9)),
            (time(13), time(12, 59)),
            (time(11, 59), time(00)),
            (time(12), time(12)),
        )
        for start_time, end_time in testcases:
            with self.subTest(
                f"Testing time validation: start time: {start_time}, end time: {end_time}",
                start_time=start_time,
                end_time=end_time,
            ):
                with self.assertRaises(ValidationError) as cm:
                    EventDetailPageFactory.build(
                        start_time=start_time,
                        end_time=end_time,
                        path="0",
                        depth=0,
                        location=EventLocationFactory(),
                        eligibility=EventEligibilityFactory(),
                    ).full_clean()

                the_exception = cm.exception
                self.assertEqual(1, len(the_exception.messages))
                self.assertEqual(
                    "The end time must come after the start time.",
                    the_exception.messages[0],
                )

    def test_event_time_required(self):
        start_time = None
        end_time = time(12, 59)
        message = "Please enter a start time."

        with self.assertRaises(ValidationError) as cm:
            EventDetailPageFactory.build(
                start_time=start_time,
                end_time=end_time,
                path="0",
                depth=0,
                location=EventLocationFactory(),
                eligibility=EventEligibilityFactory(),
            ).full_clean()

        the_exception = cm.exception

        self.assertEqual(1, len(the_exception.messages))
        self.assertEqual(message, the_exception.messages[0])

    def test_event_date_validation(self):
        start_date = date(2024, 2, 1)
        end_date = date(2024, 1, 1)
        with self.subTest(
            f"Testing date validation: start date: {start_date}, end date: {end_date}",
            start_date=start_date,
            end_date=end_date,
        ):
            with self.assertRaises(ValidationError) as cm:
                EventDetailPageFactory.build(
                    start_date=start_date,
                    end_date=end_date,
                    path="0",
                    depth=0,
                    location=EventLocationFactory(),
                    eligibility=EventEligibilityFactory(),
                ).full_clean()

            the_exception = cm.exception
            self.assertEqual(2, len(the_exception.messages))
            self.assertEqual(
                "The start date must come before the end date.",
                the_exception.messages[0],
            )
            self.assertEqual(
                "The end date must come after the start date.",
                the_exception.messages[1],
            )


class EventDetailPageRelatedContentTests(WagtailPageTestCase):
    """
    Test the values returned from the EventDetailPage.get_related_pages method
    """

    def setUp(self):
        self.editorial_type = EditorialTypeFactory()
        self.editorial_page = EditorialPageFactory(
            editorial_types=[EditorialPageTypePlacement(type=self.editorial_type)]
        )
        self.event_page = EventDetailPageFactory()
        self.guide_page = GuidePageFactory()
        self.programme_page = ProgrammePageFactory()
        self.research_page = ResearchCentrePageFactory()
        self.school_page = SchoolPageFactory(
            introduction_image=wagtail_factories.ImageFactory()
        )
        self.short_course_page = ShortCoursePageFactory()
        self.landing_page_research = ResearchLandingPageFactory()
        self.landing_page_innovation = InnovationLandingPageFactory()
        self.landing_page_ee = EELandingPageFactory()
        self.landing_page_enterprise = EnterpriseLandingPageFactory()

    def make_related_page(self, event_page, page):
        return EventDetailPageRelatedPages(source_page=event_page, page=page)

    def test_editorial_related_content_meta_value(self):
        self.event_page.related_pages = [
            self.make_related_page(self.event_page, self.editorial_page)
        ]
        self.assertEqual(
            self.event_page.get_related_pages()["items"][0]["meta"], self.editorial_type
        )

    def test_event_related_content_meta_value(self):
        self.event_page.related_pages = [
            self.make_related_page(self.event_page, self.event_page)
        ]
        self.assertEqual(
            self.event_page.get_related_pages()["items"][0]["meta"], "Event"
        )

    def test_guide_related_content_meta_value(self):
        self.event_page.related_pages = [
            self.make_related_page(self.event_page, self.guide_page)
        ]
        self.assertEqual(
            self.event_page.get_related_pages()["items"][0]["meta"], "Guide"
        )

    def test_programme_related_content_meta_value(self):
        self.event_page.related_pages = [
            self.make_related_page(self.event_page, self.programme_page)
        ]
        self.assertEqual(
            self.event_page.get_related_pages()["items"][0]["meta"], "Programme"
        )

    def test_research_related_content_meta_value(self):
        self.event_page.related_pages = [
            self.make_related_page(self.event_page, self.research_page)
        ]
        self.assertEqual(
            self.event_page.get_related_pages()["items"][0]["meta"], "Research Centre"
        )

    def test_school_related_content_meta_value(self):
        self.event_page.related_pages = [
            self.make_related_page(self.event_page, self.school_page)
        ]
        self.assertEqual(
            self.event_page.get_related_pages()["items"][0]["meta"], "School"
        )

    def test_short_course_related_content_meta_value(self):
        self.event_page.related_pages = [
            self.make_related_page(self.event_page, self.short_course_page)
        ]
        self.assertEqual(
            self.event_page.get_related_pages()["items"][0]["meta"], "Short Course"
        )

    # The landing page models shouldn't have any meta value coming through
    def test_research_landing_page_related_content_meta_value(self):
        self.event_page.related_pages = [
            self.make_related_page(self.event_page, self.landing_page_research)
        ]
        self.assertEqual(self.event_page.get_related_pages()["items"][0]["meta"], "")

    def test_innovation_landing_page_related_content_meta_value(self):
        self.event_page.related_pages = [
            self.make_related_page(self.event_page, self.landing_page_innovation)
        ]
        self.assertEqual(self.event_page.get_related_pages()["items"][0]["meta"], "")

    def test_ee_landing_page_related_content_meta_value(self):
        self.event_page.related_pages = [
            self.make_related_page(self.event_page, self.landing_page_ee)
        ]
        self.assertEqual(self.event_page.get_related_pages()["items"][0]["meta"], "")

    def test_enterprise_landing_page_related_content_meta_value(self):
        self.event_page.related_pages = [
            self.make_related_page(self.event_page, self.landing_page_enterprise)
        ]
        self.assertEqual(self.event_page.get_related_pages()["items"][0]["meta"], "")
