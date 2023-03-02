from django.conf import settings
from django.test import TestCase
from wagtail.rich_text import RichText

from rca.utils.templatetags.util_tags import is_external, richtext_force_external_links


class IsExternalTestCase(TestCase):
    def test_external_url(self):
        result = is_external("https://flying.circus.com", "https://rca.ac.uk")
        self.assertEqual(result, True)

    def test_internal_url(self):
        result = is_external("https://rca.ac.uk", "https://flying.circus.com")
        self.assertEqual(result, False)

    def test_internal_url_hash(self):
        result = is_external("#")
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
            settings.WAGTAILADMIN_BASE_URL,
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


class ForceExternalLinksFilterTest(TestCase):
    def link_maker(self):
        return "This is a <a href='test'>Link</a>"

    def test_link_target_is_external(self):
        blob = self.link_maker()
        self.assertEqual(
            richtext_force_external_links(blob),
            '<div class="rich-text">This is a <a href="test" target="_blank">Link</a></div>',
        )

    def test_multiple_link_targets_are_external(self):
        blob = self.link_maker() + self.link_maker()
        self.assertEqual(
            richtext_force_external_links(blob),
            """<div class="rich-text">This is a <a href="test" target="_blank">Link</a>"""
            """This is a <a href="test" target="_blank">Link</a></div>""",
        )

    def test_type_error_raised(self):
        with self.assertRaises(TypeError):
            self.assertEqual(richtext_force_external_links(1), "")

    def test_none_value_returns_str(self):
        self.assertEqual(
            richtext_force_external_links(value=None), '<div class="rich-text"></div>'
        )

    def test_passing_rich_text_value_has_no_effect(self):
        # passing a RichText value through the |richtext_force_external_links filter should have no effect
        value = RichText(source="")
        self.assertEqual(richtext_force_external_links(value), value)
