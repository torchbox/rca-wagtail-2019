from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from wagtail_factories import CollectionFactory

from rca.home.models import HomePage
from rca.people.factories import StudentIndexPageFactory
from rca.people.models import StudentPage
from rca.users.factories import UserFactory
from rca.users.models import User


class TestAccountManagementViews(TestCase):

    create_view_name = "student_account_create"

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
            "create_student_page": True,
            "student_user_image_collection": CollectionFactory(
                name="Student: Monty python"
            ).id,
        }
        students = Group.objects.get(name="Students")
        admin_permission = Permission.objects.get(codename="access_admin")
        students.permissions.add(admin_permission)

    def test_student_redirected(self):
        # User with a role 'student' should be redirected to their student page after login
        self.client.force_login(self.user)
        # Create the student and the page
        self.client.post(reverse(self.create_view_name), data=self.form_data)
        self.client.logout()

        student_user = User.objects.get(username="montypython")
        student_user.set_password("test")
        student_user.save()
        student_page = StudentPage.objects.get(student_user_account=student_user)

        # Login as the student
        response = self.client.post(
            "/admin/login/",
            follow=True,
            data={"username": "montypython", "password": "test"},
        )
        redirect_url = reverse(
            "wagtailadmin_pages:edit", kwargs={"page_id": student_page.id}
        )
        self.assertEqual(response.redirect_chain[0], (redirect_url, 302))
