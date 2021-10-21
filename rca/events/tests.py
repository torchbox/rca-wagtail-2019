from datetime import date

import wagtail_factories
from django.test import TestCase
from freezegun import freeze_time
from wagtail.tests.utils import WagtailPageTests

from rca.editorial.factories import EditorialPageFactory, EditorialTypeFactory
from rca.editorial.models import EditorialPageTypePlacement
from rca.guides.factories import GuidePageFactory
from rca.home.models import HomePage
from rca.landingpages.factories import (
    EELandingPageFactory,
    EnterpriseLandingPageFactory,
    InnovationLandingPageFactory,
    ResearchLandingPageFactory,
)
from rca.people.factories import DirectorateFactory
from rca.people.models import Directorate
from rca.programmes.factories import ProgrammePageFactory
from rca.research.factories import ResearchCentrePageFactory
from rca.schools.factories import SchoolPageFactory
from rca.shortcourses.factories import ShortCoursePageFactory
from rca.standardpages.models import IndexPage, InformationPage

from .factories import EventDetailPageFactory, EventSeriesFactory, EventTypeFactory
from .models import (
    EventDetailPage,
    EventDetailPageRelatedDirectorate,
    EventDetailPageRelatedPages,
    EventIndexPage,
    EventType,
)


class TestEventDetailPageFactories(TestCase):
    def test_factories(self):
        EventDetailPageFactory()


class EventDetailPageTests(WagtailPageTests):
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
        event_type = EventTypeFactory()
        event1 = EventDetailPageFactory(
            parent=home_page,
            start_date=date(2021, 1, 4),
            end_date=date(2021, 1, 5),
            series=series,
            event_type=event_type,
        )
        event2 = EventDetailPageFactory(
            parent=home_page,
            start_date=date(2021, 1, 6),
            end_date=date(2021, 1, 7),
            series=series,
            event_type=event_type,
        )
        event3 = EventDetailPageFactory(
            parent=home_page,
            start_date=date(2021, 1, 8),
            end_date=date(2021, 1, 9),
            series=series,
            event_type=event_type,
        )
        event4 = EventDetailPageFactory(
            parent=home_page,
            start_date=date(2021, 1, 1),
            end_date=date(2021, 1, 2),
            series=series,
            event_type=event_type,
        )
        # different series, should not show
        EventDetailPageFactory(
            parent=home_page,
            start_date=date(2021, 1, 6),
            end_date=date(2021, 1, 7),
            series=EventSeriesFactory(),
            event_type=event_type,
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


class EventDetailPageDateTests(WagtailPageTests):
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
            event_type=EventTypeFactory(),
        )
        self.assertEqual(one_day_event.event_date_short, "6 January 2021")

    def test_same_month_event(self):
        same_month_event = EventDetailPageFactory(
            parent=self.home_page,
            start_date=date(2021, 1, 6),
            end_date=date(2021, 1, 9),
            series=EventSeriesFactory(),
            event_type=EventTypeFactory(),
        )
        self.assertEqual(same_month_event.event_date_short, "6 - 9 January 2021")

    def test_different_month_event(self):
        different_month_event = EventDetailPageFactory(
            parent=self.home_page,
            start_date=date(2021, 1, 6),
            end_date=date(2021, 2, 9),
            series=EventSeriesFactory(),
            event_type=EventTypeFactory(),
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
            event_type=EventTypeFactory(),
        )
        self.assertEqual(
            different_year_event.event_date_short, "29 December 2021 - 1 January 2022"
        )


class EventDetailPageRelatedContentTests(WagtailPageTests):
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


class EventSerializerTests(WagtailPageTests):
    def setUp(self):
        self.home_page = HomePage.objects.first()
        self.event_page = EventDetailPageFactory(
            parent=self.home_page, event_type=EventTypeFactory(),
        )

    def test_api_response_for_event(self):
        response = self.client.get(f"/api/v3/pages/{self.event_page.id}/")
        self.assertEqual(response.status_code, 200)

    def test_api_response_for_event_with_null_type(self):
        event_type = EventType.objects.get(id=self.event_page.event_type.id)
        event_type.delete()
        self.event_page.refresh_from_db()
        response = self.client.get(f"/api/v3/pages/{self.event_page.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["event_type"], None)

    def test_api_response_for_event_with_null_directorate(self):
        # Add a directorate that relates to the page
        directorate = DirectorateFactory()
        self.event_page.related_directorates = [
            EventDetailPageRelatedDirectorate(
                source_page=self.event_page, directorate=directorate
            )
        ]
        self.event_page.save()
        # Check the directorate is there
        response = self.client.get(f"/api/v3/pages/{self.event_page.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["related_directorates"][0]["title"], directorate.title
        )

        # Delete the directorate
        directorate = Directorate.objects.get(
            id=self.event_page.related_directorates.first().directorate.id
        )
        directorate.delete()

        # Assert there are no related directorates
        self.assertQuerysetEqual(self.event_page.related_directorates.all(), [])
        response = self.client.get(f"/api/v3/pages/{self.event_page.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["related_directorates"], [])


# TODO
# The intranet integration depends on the api structure remaining intact.
# we need to write tests to confirm it fails if changed
