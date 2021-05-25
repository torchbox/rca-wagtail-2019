from django.contrib.auth.models import Group
from django.test import TestCase
from wagtail.core.models import (
    Collection,
    GroupCollectionPermission,
    GroupPagePermission,
    Permission,
)
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

        self.student = User.objects.create_user(
            username="danascully",
            first_name="dana",
            last_name="Scully",
            email="ds@fbi.com",
            password="1234",
        )
        self.collection = CollectionFactory(name="Student: dana scully")

        student_group = Group.objects.get(name="Students")
        # Add the student group
        self.student.groups.add(student_group)
        self.student.save()

    def test_creating_creates_permision_group(self):
        """Creating a student page WITH a student user account and student image
        collection value should generate a group with permission on page.save()
        """
        self.student_index.add_child(
            instance=StudentPage(
                title="Dana Scully",
                slug="a-student",
                first_name="dana",
                last_name="student",
                student_user_image_collection=self.collection,
                student_user_account=self.student,
            )
        )
        student_page = StudentPage.objects.get(slug="a-student")
        group = Group.objects.get(name=f"Student: {self.student.username}")
        page_permission = GroupPagePermission.objects.filter(
            group=group, page=student_page, permission_type="edit"
        )
        edit_collection_permission = GroupCollectionPermission.objects.get(
            group=group,
            collection=Collection.objects.get(name=self.collection),
            permission=Permission.objects.get(codename="add_image"),
        )
        choose_collection_permission = GroupCollectionPermission.objects.get(
            group=group,
            collection=Collection.objects.get(name=self.collection),
            permission=Permission.objects.get(codename="choose_image"),
        )
        self.assertTrue(group)
        self.assertTrue(page_permission)
        self.assertTrue(edit_collection_permission)
        self.assertTrue(choose_collection_permission)

    def test_creating_does_not_create_permision_group(self):
        """Creating a student page WITHOUT a student user account and student image
        collection value should NOT generate a group with permission on page.save()
        """
        self.student_index.add_child(
            instance=StudentPage(
                title="Dana Scully",
                slug="a-student",
                first_name="dana",
                last_name="student",
            )
        )
        group = Group.objects.filter(name=f"Student: {self.student.username}")
        self.assertFalse(group)
