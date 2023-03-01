from django.test import TestCase
from wagtail.test.utils import WagtailPageTestCase

from rca.editorial.factories import (
    AuthorFactory,
    EditorialListingPageFactory,
    EditorialPageFactory,
    EditorialTypeFactory,
)
from rca.editorial.models import (
    EditorialListingPage,
    EditorialPage,
    EditorialPageTypePlacement,
)
from rca.home.models import HomePage
from rca.standardpages.models import IndexPage, InformationPage


class TestEditorialFactories(TestCase):
    def test_factories(self):
        EditorialPageFactory()
        AuthorFactory()
        # Test with type
        type = EditorialTypeFactory()
        EditorialPageFactory(editorial_types=[EditorialPageTypePlacement(type=type)])


class EditorialListingPageTests(WagtailPageTestCase):
    def test_can_add_only_editorial_child_pages(self):
        self.assertCanNotCreateAt(EditorialListingPage, InformationPage)
        self.assertCanNotCreateAt(EditorialListingPage, IndexPage)

    def test_can_add_editorial_child_page(self):
        self.assertCanCreateAt(EditorialListingPage, EditorialPage)

    def test_does_not_show_editorial_pages_when_show_in_index_page_not_toggled(self):
        home_page = HomePage.objects.get()
        editorial_listing_page = EditorialListingPageFactory(parent=home_page)
        editorial_page = EditorialPageFactory(parent=editorial_listing_page)

        resp = self.client.get(editorial_listing_page.url)
        self.assertContains(resp, editorial_page.title)

        editorial_page.show_in_index_page = False
        editorial_page.save()

        resp = self.client.get(editorial_listing_page.url)
        self.assertNotContains(resp, editorial_page.title)
