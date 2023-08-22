import wagtail_factories
from django.urls import reverse
from wagtail.test.utils import WagtailPageTestCase

from rca.home.models import HomePage
from rca.schools.factories import SchoolPageFactory


class TestSchoolPageFactory(WagtailPageTestCase):
    def test_factories(self):
        SchoolPageFactory(introduction_image=wagtail_factories.ImageFactory())


class TestSchoolPage(WagtailPageTestCase):
    def setUp(self):
        self.home_page = HomePage.objects.first()
        self.school_page = SchoolPageFactory(
            introduction_image=wagtail_factories.ImageFactory(), parent=self.home_page
        )

    def test_school_page_404s(self):
        # Logged out user should receive a 404
        response = self.client.get(self.school_page.url)
        self.assertEqual(response.status_code, 404)

    def test_school_page_200(self):
        # Superuser should be able to see the page
        self.login()
        response = self.client.get(self.school_page.url)
        self.assertEqual(response.status_code, 200)

    def test_school_page_preview_200s(self):
        # Superuser should be able to preview
        self.login()
        preview_url = reverse(
            "wagtailadmin_pages:preview_on_edit", args=(self.school_page.id,)
        )
        response = self.client.get(preview_url)
        self.assertEqual(response.status_code, 200)

    def test_school_page_preview_302s(self):
        # Logged out used should raise 302 when requesting preview
        preview_url = reverse(
            "wagtailadmin_pages:preview_on_edit", args=(self.school_page.id,)
        )
        response = self.client.get(preview_url)
        self.assertEqual(response.status_code, 302)
