from django.test import TestCase
from wagtail.tests.utils import WagtailPageTests

from rca.home.models import HomePage
from rca.standardpages.models import IndexPage, InformationPage

from .factories import EditorialPageFactory, EditorialTypeFactory
from .models import (
    EditorialListingPage,
    EditorialPage,
    EditorialPageTypePlacement,
    EditorialType,
)


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


class EditorialSerializerTests(WagtailPageTests):
    def setUp(self):
        self.home_page = HomePage.objects.first()
        self.editorial_page = EditorialPageFactory(parent=self.home_page,)

    def test_api_response_for_editorial(self):
        response = self.client.get(f"/api/v3/pages/{self.editorial_page.id}/")
        self.assertEqual(response.status_code, 200)

    def test_api_response_for_editorial_with_type(self):
        editorial_type = EditorialTypeFactory()
        self.editorial_page.editorial_types = [
            EditorialPageTypePlacement(page=self.editorial_page, type=editorial_type)
        ]
        self.editorial_page.save()
        response = self.client.get(f"/api/v3/pages/{self.editorial_page.id}/")
        self.assertEqual(response.status_code, 200)
        # Check the directorate is there
        self.assertEqual(
            response.data["editorial_types"][0]["title"], editorial_type.title
        )

    def test_api_response_for_editorial_with_deleted_type(self):
        editorial_type = EditorialTypeFactory()
        self.editorial_page.editorial_types = [
            EditorialPageTypePlacement(page=self.editorial_page, type=editorial_type)
        ]
        self.editorial_page.save()
        response = self.client.get(f"/api/v3/pages/{self.editorial_page.id}/")
        self.assertEqual(response.status_code, 200)
        # Check the directorate is there
        self.assertEqual(
            response.data["editorial_types"][0]["title"], editorial_type.title
        )

        # Delete the type
        type = EditorialType.objects.get(
            id=self.editorial_page.editorial_types.first().type.id
        )
        type.delete()
        response = self.client.get(f"/api/v3/pages/{self.editorial_page.id}/")
        self.assertEqual(response.status_code, 200)
        # Check the directorate is there
        self.assertEqual(response.data["editorial_types"], [])
