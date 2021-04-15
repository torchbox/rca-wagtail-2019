from django.contrib.auth.models import Group
from django.test import TestCase

from rca.home.models import HomePage
from rca.people.models import StudentIndexPage, StudentPage
from rca.users.factories import UserFactory
from rca.users.models import User


class TestUserFactory(TestCase):
    def test_factories(self):
        UserFactory()


class TestStudentIndexPage(TestCase):
    def setUp(self):
        self.home_page = HomePage.objects.first()
        self.home_page.add_child(
            instance=StudentIndexPage(
                title="Students", slug="students", introduction="students",
            )
        )
        self.student_index = StudentIndexPage.objects.first()

    def test_creating_a_student_creates_a_page(self):
        # Creating a user account with the role 'student' should create
        # a StudentPage with the same first and last name.
        student_group = Group.objects.get(name="Students")
        student_user = User.objects.create_user(
            username="test_student",
            password="12345",
            first_name="Fox",
            last_name="Mulder",
        )
        student_user.groups.add(student_group)
        student_page = StudentPage.objects.get(student_user_account=student_user)
        # Confirm that a page was created with the student user detials and relationship.
        self.assertEqual(student_page.first_name, student_user.first_name)
        self.assertEqual(student_page.last_name, student_user.last_name)
        self.assertEqual(student_page.student_user_account, student_user)
        self.assertEqual(student_page.live, False)

    def test_creating_a_user_checks_for_existing_page(self):
        # If a student page matching a users first and last name is being added then we
        # don't want to create a duplicate page.
        self.student_index.add_child(
            instance=StudentPage(
                title="Dana Scully", first_name="Dana", last_name="Scully",
            )
        )
        student_group = Group.objects.get(name="Students")
        student_user = User.objects.create_user(
            username="test_student",
            password="12345",
            first_name="Dana",
            last_name="Scully",
        )
        student_user.groups.add(student_group)
        self.assertEqual(len(StudentPage.objects.all()), 1)

    def test_deleting_student_account(self):
        # When a student account is deleted, the relationship on the student page
        # should be removed but the page should still exist.
        student_group = Group.objects.get(name="Students")
        student_user = User.objects.create_user(
            username="test_student",
            password="12345",
            first_name="Monty",
            last_name="Python",
        )
        student_user.groups.add(student_group)
        self.assertEqual(len(StudentPage.objects.all()), 1)
        student_page = StudentPage.objects.get(title="Monty Python")
        self.assertEqual(student_page.student_user_account, student_user)
        student_user.delete()
        student_page.refresh_from_db()
        self.assertEqual(student_page.student_user_account, None)
