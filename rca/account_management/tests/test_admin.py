from bs4 import BeautifulSoup as bs4
from django.contrib.auth.models import Group, Permission
from django.test import TestCase

from rca.users.factories import UserFactory


class TestStudentAdmin(TestCase):
    """
    We make some changes to the admin interface if the user is a student.
    This test is making sure the admin search is removed for sutdents,
    editors and admins should still see the search.
    """

    def setUp(self):
        self.user = UserFactory(is_superuser=True)
        student_group = Group.objects.get(name="Students")
        editor_group = Group.objects.get(name="Editors")
        self.student_user = UserFactory()
        self.student_user.groups.add(student_group)
        self.editor = UserFactory()
        self.editor.groups.add(editor_group)

        admin_permission = Permission.objects.get(codename="access_admin")
        student_group.permissions.add(admin_permission)
        self.student_user.save()

    def test_search_is_visible_for_superusers(self):
        self.client.force_login(self.user)
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

        soup = bs4(response.content, "html.parser")
        sidebar = soup.find("aside")
        self.assertIsNotNone(sidebar)
        self.assertFalse("data-student-sidebar" in sidebar.attrs)

    def test_search_is_visible_for_editors(self):
        self.client.force_login(self.editor)
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        soup = bs4(response.content, "html.parser")
        sidebar = soup.find("aside")
        self.assertIsNotNone(sidebar)
        self.assertFalse("data-student-sidebar" in sidebar.attrs)

    def test_search_is_not_visible_for_students(self):
        self.client.force_login(self.student_user)
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

        soup = bs4(response.content, "html.parser")
        sidebar = soup.find("aside")
        self.assertIsNotNone(sidebar)
        self.assertTrue("data-student-sidebar" in sidebar.attrs)
