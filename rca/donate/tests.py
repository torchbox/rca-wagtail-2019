from django.test import TestCase

from rca.donate.factories import DonationFormPageFactory


class TestDonationFormPageFactory(TestCase):
    def test_factories(self):
        DonationFormPageFactory()
