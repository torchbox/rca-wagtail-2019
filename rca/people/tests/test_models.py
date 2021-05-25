from django.test import TestCase
from wagtail.tests.utils import WagtailPageTests
from wagtail_factories import CollectionFactory

from rca.home.models import HomePage
from rca.people.factories import StudentIndexPageFactory, StudentPageFactory
from rca.people.models import StudentIndexPage, StudentPage
from rca.users.models import User


class TestStudentPageFactory(TestCase):
    def test_factories(self):
        StudentPageFactory()
        StudentIndexPageFactory()


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


class TestStudentPage(WagtailPageTests):
    def setUp(self):
        super().setUp()
        self.home_page = HomePage.objects.first()
        self.home_page.add_child(
            instance=StudentIndexPage(
                title="Students", slug="students", introduction="Students"
            )
        )
        self.student_index = StudentIndexPage.objects.first()

    def test_creating_creates_permision_group(self):
        self.student = User.objects.create_user(
            username="danascully",
            first_name="dana",
            last_name="Scully",
            email="ds@fbi.com",
            password="1234",
        )
        self.student.save()
        self.collection = CollectionFactory(name="Student: dana scully")

        self.student_index.add_child(
            instance=StudentPage(
                title="Dana Scully",
                slug="a-student",
                first_name="dana",
                last_name="student",
                student_user_image_collection=self.collection,
                student_user_account=self.student
                # {'student_user_account': ['user instance with id 3 does not exist.']}
                # I do not understand why, I can see it exists!
            )
        )
        self.assertTrue(False)
