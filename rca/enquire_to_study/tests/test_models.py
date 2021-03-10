from wagtail.tests.utils import WagtailPageTests

from rca.enquire_to_study.factories import StartDateFactory


class TestEnquireFormFactoriesFactories(WagtailPageTests):
    def test_factories(self):
        StartDateFactory()
