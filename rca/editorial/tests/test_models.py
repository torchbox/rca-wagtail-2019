from django.test import TestCase
from wagtail.test.utils import WagtailPageTestCase

from rca.editorial.factories import (
    AuthorFactory,
    EditorialPageFactory,
    EditorialTypeFactory,
)
from rca.editorial.models import (
    EditorialListingPage,
    EditorialPage,
    EditorialPageTypePlacement,
)
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
