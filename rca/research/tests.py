from django.test import TestCase

from .factories import ResearchCentrePageFactory


class TestResearchCentrePageFactories(TestCase):
    def test_factories(self):
        ResearchCentrePageFactory()
