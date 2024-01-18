from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from wagtail.models import GroupPagePermission
from wagtail.test.utils import WagtailTestUtils

from rca.home.models import HomePage
from rca.people.models import StudentIndexPage, StudentPage
from rca.users.factories import UserFactory


class TestPerRequestEditHandler(TestCase, WagtailTestUtils):
    def setUp(self):
        # Find root page
        self.student = UserFactory(username="student")
        self.user = UserFactory(is_superuser=True)
        self.student_group = Group.objects.get(name="Students")
        admin_permission = Permission.objects.get(codename="access_admin")
        self.student_group.permissions.add(admin_permission)
        self.student.groups.add(self.student_group)
        self.student.set_password("test")
        self.student.save()

        self.home_page = HomePage.objects.first()
        self.home_page.add_child(
            instance=StudentIndexPage(
                title="Students",
                slug="students",
                introduction="students",
            )
        )
        self.student_index = StudentIndexPage.objects.first()
        GroupPagePermission.objects.create(
            group=self.student_group,
            page=self.student_index,
            permission=Permission.objects.get(
                content_type__app_label="wagtailcore", codename="change_page"
            ),
        )
        self.student_index.add_child(
            instance=StudentPage(
                title="A student", slug="a-student", first_name="a", last_name="student"
            )
        )
        self.student_page = StudentPage.objects.first()

    def test_create_page_with_per_request_custom_edit_handlers(self):
        """
        Test that per-request custom behaviour in edit handlers is honoured
        """
        # non-superusers should not see secret_data
        self.client.force_login(self.student)
        response = self.client.get(
            reverse("wagtailadmin_pages:edit", args=(self.student_page.id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"profile_image"')
        self.assertNotContains(response, '"student_user_account"')

        # superusers should see secret_data
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("wagtailadmin_pages:edit", args=(self.student_page.id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"profile_image"')
        self.assertContains(response, '"student_user_account"')
