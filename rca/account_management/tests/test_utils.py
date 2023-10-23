from django.test import TestCase

from rca.account_management.utils import get_set_password_url
from rca.users.factories import UserFactory


class TestAccountManagementUtils(TestCase):
    def test_set_password_reset_link(self):
        user = UserFactory()
        reset_link = get_set_password_url(user)
        self.assertRegex(
            reset_link,
            r"^/admin/password_reset/confirm/([0-9A-Za-z_\-]+)/([0-9A-Za-z]{1,6}-[0-9A-Za-z]{8,32})",
        )
