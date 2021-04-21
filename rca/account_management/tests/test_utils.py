from django.test import TestCase

from rca.account_management.utils import get_set_password_url
from rca.users.factories import UserFactory


class TestAccountManagementUtils(TestCase):
    def test_set_password_reset_link(self):
        user = UserFactory()
        reset_link = get_set_password_url(user)
        self.assertTrue(reset_link)
