from wagtail.tests.utils import WagtailPageTests

from rca.home.models import HomePage
from rca.standardpages.models import IndexPage, InformationPage

from .models import ProgrammeIndexPage, ProgrammePage


class ProgrammePageTests(WagtailPageTests):
    def test_can_create_under_programme_index_page(self):
        self.assertCanCreateAt(ProgrammeIndexPage, ProgrammePage)

    def test_cant_create_under_other_pages(self):
        self.assertCanNotCreateAt(IndexPage, ProgrammePage)
        self.assertCanNotCreateAt(InformationPage, ProgrammePage)
        self.assertCanNotCreateAt(HomePage, ProgrammePage)
