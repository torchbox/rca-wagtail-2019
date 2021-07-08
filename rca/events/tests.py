from wagtail.tests.utils import WagtailPageTests

from rca.home.models import HomePage
from rca.standardpages.models import IndexPage, InformationPage

from .models import EventDetailPage, EventIndexPage


class EventDetailPageTests(WagtailPageTests):
    def test_can_create_under_event_index_page(self):
        self.assertCanCreateAt(EventIndexPage, EventDetailPage)

    def test_cant_create_under_other_pages(self):
        self.assertCanNotCreateAt(IndexPage, EventDetailPage)
        self.assertCanNotCreateAt(InformationPage, EventDetailPage)
        self.assertCanNotCreateAt(HomePage, EventDetailPage)
