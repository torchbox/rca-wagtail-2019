from django.test import TestCase

from .factories import GuidePageFactory


class TestGuidePageFactories(TestCase):
    def test_factories(self):
        GuidePageFactory()
