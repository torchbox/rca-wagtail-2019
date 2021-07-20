from datetime import date

from freezegun import freeze_time
from wagtail.tests.utils import WagtailPageTests

from rca.home.models import HomePage
from rca.standardpages.models import IndexPage, InformationPage

from .factories import EventDetailPageFactory, EventSeriesFactory, EventTypeFactory
from .models import EventDetailPage, EventIndexPage


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
