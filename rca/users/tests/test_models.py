from django.test import TestCase

from rca.users.factories import UserFactory


class TestUserFactory(TestCase):
    def test_factories(self):
        UserFactory()
