from django.test import TestCase
from django.urls import reverse

from rca.account_management.forms import StudentCreateForm
from rca.home.models import HomePage
from rca.people.factories import StudentIndexPageFactory
from rca.people.models import StudentPage
from rca.users.factories import UserFactory
from rca.users.models import User


class TestStudentAccountCreationForm(TestCase):

    view_name = "student_account_create"

    def setUp(self):
        self.user = UserFactory(is_superuser=True)
        self.home_page = HomePage.objects.first()
        self.student_index = StudentIndexPageFactory(
            parent=self.home_page,
            title="Students",
            slug="students",
            introduction="students",
        )
        self.form_data = {
            "first_name": "Monty",
            "last_name": "python",
            "email": "monthpython@holygrail.com",
            "username": "montypython",
            "create_student_page": False,
        }

    def test_form_302(self):
        # non superusers shouldn't be able to request the form
        self.client.logout()
        response = self.client.get(reverse(self.view_name))
        self.assertEqual(response.status_code, 302)

    def test_students_cannot_create_students(self):
        # Students shouldn't be able to use this form
        self.client.force_login(self.user)
        self.client.post(reverse(self.view_name), data=self.form_data)
        student_user = User.objects.get(username="montypython")
        self.client.force_login(student_user)
        response = self.client.get(reverse(self.view_name))
        self.assertEqual(response.status_code, 302)

    def test_form_responds_to_path_for_admin(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse(self.view_name))
        self.assertEqual(response.status_code, 200)

    def test_invalid_form(self):
        form = StudentCreateForm(data={})
        self.assertFalse(form.is_valid())

    def test_valid_form(self):
        form = StudentCreateForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_user_created(self):
        # User should have role 'student'
        self.client.force_login(self.user)
        self.assertEqual(len(User.objects.filter(username="montypython")), 0)
        self.client.post(reverse(self.view_name), data=self.form_data)
        # Check the student was created and the 'students' group was added to the user.
        self.assertEqual(len(User.objects.filter(username="montypython")), 1)
        user = User.objects.get(username="montypython")
        self.assertTrue(user.groups.filter(name="Students").exists())

    def test_creating_a_student_does_not_create_a_page(self):
        # Creating a user account with no create_student_page option
        # should not create a StudentPage object
        self.client.force_login(self.user)
        self.assertEqual(len(User.objects.filter(username="montypython")), 0)
        self.client.post(reverse(self.view_name), data=self.form_data)
        # Check the student was created
        self.assertEqual(len(User.objects.filter(username="montypython")), 1)
        # Check there isn't a student page
        self.assertEqual(len(StudentPage.objects.all()), 0)

    def test_creating_a_student_does_create_a_page(self):
        # Creating a user account with no create_student_page=True option
        # should create a StudentPage object
        self.client.force_login(self.user)
        self.assertEqual(len(User.objects.filter(username="montypython")), 0)
        self.assertEqual(len(StudentPage.objects.all()), 0)
        data = self.form_data
        data["create_student_page"] = True
        self.client.post(reverse(self.view_name), data=data)
        # Check the student was created
        self.assertEqual(len(User.objects.filter(username="montypython")), 1)
        # Check there is a student page
        self.assertEqual(len(StudentPage.objects.all()), 1)
        student_user = User.objects.get(username="montypython")
        student_page = StudentPage.objects.get(student_user_account=student_user)
        # Confirm that a page was created with the student user detials and relationship.
        self.assertEqual(student_page.first_name, student_user.first_name)
        self.assertEqual(student_page.last_name, student_user.last_name)
        self.assertEqual(student_page.student_user_account, student_user)
        self.assertEqual(student_page.live, False)
