from django.test import TestCase
from wagtail.tests.utils import WagtailPageTests

from rca.home.models import HomePage
from rca.people.factories import StudentPageFactory
from rca.people.models import StudentIndexPage


class TestStudentPageFactory(TestCase):
    def test_factories(self):
        StudentPageFactory()


class TestStudentIndexPage(WagtailPageTests):
    def setUp(self):
        self.home_page = HomePage.objects.first()
        self.user = self.login()

    def test_page_count_rules(self):
        # Only a single Student listing page should be creatable.
        # It's tied to signing up students, see rca.users.signals
        self.assertTrue(StudentIndexPage.can_create_at(self.home_page))
        self.home_page.add_child(
            instance=StudentIndexPage(
                title="Students", slug="students", introduction="Students"
            )
        )
        # A second person listing page should not be creatable
        self.assertFalse(StudentIndexPage.can_create_at(self.home_page))
