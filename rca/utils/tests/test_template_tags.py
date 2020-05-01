from django.conf import settings
from django.test import TestCase

from rca.utils.templatetags.util_tags import is_external


class IsExternalTestCase(TestCase):
    def test_external_url(self):
        result = is_external("https://flying.circus.com", "https://rca.ac.uk")
        self.assertEqual(result, True)

    def test_internal_url(self):
        result = is_external("https://rca.ac.uk", "https://flying.circus.com")
        self.assertEqual(result, False)

    def test_internal_first_multiple_url(self):
        result = is_external(
            "https://rca.ac.uk",
            "https://flying.circus.com",
            "https://rca.ac.uk",
            "https://flying.circus.com",
        )
        self.assertEqual(result, False)

    def test_all_internals(self):
        # all the internal domains with protocol should return false
        domains_with_protocol = [
            settings.BASE_URL,
            "https://rca-production.herokuapp.com/monty",
            "https://rca-staging.herokuapp.com/python",
            "https://rca-development.herokuapp.com/and",
            "https://rca.ac.uk/the",
            "https://www.rca.ac.uk/holy",
            "http://0.0.0.0/grail",
        ]
        for n in domains_with_protocol:
            result = is_external(n)
            self.assertEqual(result, False)
