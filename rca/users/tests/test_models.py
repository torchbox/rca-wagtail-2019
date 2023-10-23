from django.contrib.auth.models import Group
from django.test import TestCase

from rca.users.factories import UserFactory


class TestUserFactory(TestCase):
    def test_factories(self):
        UserFactory()


class TestUserModel(TestCase):
    def setUp(self):
        self.student_user = UserFactory()
        self.student_group = Group.objects.get(name="Students")
        self.student_user.groups.add(self.student_group)
        self.student_user.save()

    def test_is_student(self):
        self.assertTrue(self.student_user.is_student())

    def test_is_not_student(self):
        self.student_user.groups.remove(self.student_group)
        self.assertFalse(self.student_user.is_student())
