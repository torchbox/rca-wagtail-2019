import re

from django.contrib.auth.models import Group, Permission
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from wagtail.models import Collection, GroupCollectionPermission, GroupPagePermission
from wagtail_factories import CollectionFactory

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
        self.collection = CollectionFactory(name="Student: Monty python")
        self.form_data = {
            "first_name": "Monty",
            "last_name": "python",
            "email": "monthpython@holygrail.com",
            "username": "montypython",
            "create_student_page": False,
            "student_user_image_collection": self.collection.id,
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
        self.assertTrue(user.is_student())

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
        # should create a StudentPage object, with a group
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
        # Confirm that a page was created with the student user details and relationship.
        self.assertEqual(student_page.first_name, student_user.first_name)
        self.assertEqual(student_page.last_name, student_user.last_name)
        self.assertEqual(student_page.student_user_account, student_user)
        self.assertEqual(student_page.live, False)
        # Check the group and permissions were created
        group = Group.objects.get(name=f"Student: {student_user.username}")
        page_permission = GroupPagePermission.objects.filter(
            group=group,
            page=student_page,
            permission=Permission.objects.get(
                content_type__app_label="wagtailcore", codename="change_page"
            ),
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

    @override_settings(PASSWORD_RESET_TIMEOUT=60 * 60 * 24 * 30)
    def test_email_sent_with_correct_days(self):
        self.client.force_login(self.user)
        form_data = self.form_data
        form_data["create_student_page"] = True
        self.client.post(reverse(self.view_name), data=form_data)

        self.assertEqual(len(mail.outbox), 1)

        # Check that the email body contains the correct number of days
        expected_days = "30 days"
        self.assertIn(
            f"Note that this link will expire in {expected_days}.", mail.outbox[0].body
        )

    @override_settings(PASSWORD_RESET_TIMEOUT=60 * 60 * 24 * 30)
    def test_password_reset_link_expires_after_correct_days(self):
        self.client.force_login(self.user)
        form_data = self.form_data
        form_data["create_student_page"] = True
        self.client.post(reverse(self.view_name), data=self.form_data)

        email_body = mail.outbox[0].body
        # get the password reset link from the email body
        url_pattern = re.compile(r"https?://\S+")
        matches = url_pattern.findall(email_body)
        # the assumption is that there's only one link in the email body
        password_reset_link = matches[0]
        print(password_reset_link)

        self.client.logout()
        error_message = b"Invalid password reset link"

        # Check that the password reset link is valid
        future_date = timezone.now() + timezone.timedelta(days=25)
        with freeze_time(lambda: future_date):
            response = self.client.get(password_reset_link)
            self.assertNotIn(error_message, response.content)

        # Check that the password reset link is invalid after the timeout period
        future_date = timezone.now() + timezone.timedelta(days=31)
        with freeze_time(lambda: future_date):
            response = self.client.get(password_reset_link)
            self.assertIn(error_message, response.content)
