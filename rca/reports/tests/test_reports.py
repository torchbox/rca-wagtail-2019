from datetime import timedelta

from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from wagtail.models import GroupPagePermission, Page
from wagtail.test.utils import WagtailTestUtils

from rca.editorial.factories import EditorialPageFactory


class TestAgingPagesView(WagtailTestUtils, TestCase):
    def setUp(self):
        self.user = self.login()
        self.root = Page.objects.first()
        self.home = Page.objects.get(slug="home").specific
        self.home.strapline = "This is a strapline"

    def get(self, params={}):
        return self.client.get(reverse("rca_aging_pages_report"), params)

    def publish_home_page(self):
        self.home.save_revision().publish(user=self.user)

    def test_simple(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "wagtailadmin/reports/aging_pages_results.html"
        )

    def test_displays_only_published_pages(self):
        response = self.get()
        self.assertContains(response, "No pages found.")

        self.publish_home_page()
        response = self.get()

        # Home Page should be listed
        self.assertContains(response, self.home.title)
        # Last published by user is set
        self.assertContains(response, self.user.get_username())

        self.assertNotContains(response, self.root.title)
        self.assertNotContains(response, "No pages found.")

    def test_permissions(self):
        # Publish home page
        self.publish_home_page()

        # Remove privileges from user
        self.user.is_superuser = False
        self.user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="wagtailadmin", codename="access_admin"
            )
        )
        self.user.save()

        response = self.get()
        self.assertEqual(response.status_code, 302)

        # Add minimal permissions to the same user
        group = Group.objects.create(name="test group")
        GroupPagePermission.objects.create(
            group=group,
            page=Page.objects.first(),
            permission_type="add",
        )
        self.user.groups.add(group)

        response = self.get()
        self.assertEqual(response.status_code, 200)

    def test_csv_export(self):
        self.publish_home_page()

        # Set `last_published_at` to predictable value
        self.home.last_published_at = "2013-01-01T12:00:00.000Z"
        self.home.save()

        # Publish more pages, so we can check for n+1 query issues
        # and support for null 'last_published_by_user' values
        for i in range(1, 10):
            EditorialPageFactory(
                parent=self.home,
                title=f"Subpage {i}",
                last_published_at=self.home.last_published_at + timedelta(days=i),
            )

        # Request report as CSV
        with self.assertNumQueries(9):
            response = self.get(params={"export": "csv"})
        self.assertEqual(response.status_code, 200)

        # Test CSV contents
        data_lines = response.getvalue().decode().split("\n")
        self.assertEqual(
            data_lines[0], "Title,URL,Status,Last published at,Last published by,Type\r"
        )
        self.assertEqual(
            data_lines[1],
            f"Home,http://localhost/,live + draft,2013-01-01 12:00:00+00:00,test@email.com,Home page\r",  # noqa E501
        )
