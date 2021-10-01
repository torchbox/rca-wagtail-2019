from django.test import TestCase
from wagtail.tests.utils import WagtailPageTests

from rca.standardpages.models import IndexPage, InformationPage

from .factories import EditorialPageFactory, EditorialTypeFactory
from .models import EditorialListingPage, EditorialPage, EditorialPageTypePlacement


class TestEditorialFactories(TestCase):
    def test_factories(self):
        EditorialPageFactory()
        # Test with type
        type = EditorialTypeFactory()
        EditorialPageFactory(editorial_types=[EditorialPageTypePlacement(type=type)])


class EditorialListingPageTests(WagtailPageTests):
    def test_can_add_only_editorial_child_pages(self):
        self.assertCanNotCreateAt(EditorialListingPage, InformationPage)
        self.assertCanNotCreateAt(EditorialListingPage, IndexPage)

    def test_can_add_editorial_child_page(self):
        self.assertCanCreateAt(EditorialListingPage, EditorialPage)
