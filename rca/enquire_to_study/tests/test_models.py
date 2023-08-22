from wagtail.test.utils import WagtailPageTestCase

from rca.enquire_to_study.factories import StartDateFactory


class TestEnquireFormFactoriesFactories(WagtailPageTestCase):
    def test_factories(self):
        StartDateFactory()
