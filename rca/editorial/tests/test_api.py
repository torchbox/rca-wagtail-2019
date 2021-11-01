from wagtail.tests.utils import WagtailPageTests

from rca.editorial.factories import EditorialPageFactory, EditorialTypeFactory
from rca.editorial.models import EditorialPageTypePlacement, EditorialType
from rca.home.models import HomePage


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
