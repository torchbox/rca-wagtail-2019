from django.test import TestCase
from wagtail.tests.utils import WagtailPageTests
from wagtail_factories import CollectionFactory

from rca.home.models import HomePage
from rca.people.factories import StudentIndexPageFactory, StudentPageFactory
from rca.people.models import StudentIndexPage
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
        self.home_page = HomePage.objects.first()
        self.user = self.login()
        self.home_page.add_child(
            instance=StudentIndexPage(
                title="Students", slug="students", introduction="Students"
            )
        )
        self.student = User.objects.create(
            username="danascully",
            first_name="dana",
            last_name="Scully",
            email="ds@fbi.com",
            password="1234",
        )

        self.collection = CollectionFactory(name="Student: dana scully")

    # def test_validation_of_user_field(self):
    #     # on saving a student page with an image collection and student user,
    #     # we expect to see a group with permissions added
    #     self.student_index = StudentIndexPage.objects.first()
    #     self.student_index.add_child(
    #         instance=StudentPageFactory(
    #             title="Dana Scully",
    #             slug="a-student",
    #             first_name="dana",
    #             last_name="student",
    #             student_user_account=self.student,
    #         )
    #     )
    #     self.assertTrue(False)

    # def test_group_and_rules_creation_on_save(self):
    #     # on saving a student page with an image collection and student user,
    #     # we expect to see a group with permissions added
    #     # self.student.save()
    #     # print(self.student)
    #     self.student_index = StudentIndexPage.objects.first()
    #     self.student_index.add_child(
    #         instance=StudentPage(
    #             title="Dana Scully",
    #             slug="a-student",
    #             first_name="dana",
    #             last_name="student",
    #             student_user_account=self.student,
    #             student_user_image_collection = self.collection
    #         )
    #     )
    #     print(StudentPage.objects.filter(title="Dana Scully"))
    #     self.assertTrue(False)
