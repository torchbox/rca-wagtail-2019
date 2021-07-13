from datetime import date

from freezegun import freeze_time
from wagtail.tests.utils import WagtailPageTests

from rca.home.models import HomePage
from rca.standardpages.models import IndexPage, InformationPage

from .factories import EventDetailPageFactory, EventSeriesFactory
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
        # old event, should not show
        EventDetailPageFactory(
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
                }
            ],
            event1.get_series_events(),
        )
