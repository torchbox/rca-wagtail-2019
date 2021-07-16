from wagtail.tests.utils import WagtailPageTests

from rca.standardpages.models import IndexPage, InformationPage

from .models import EditorialListingPage, EditorialPage


class EditorialListingPageTests(WagtailPageTests):
    def test_can_add_only_editorial_child_pages(self):
        self.assertCanNotCreateAt(EditorialListingPage, InformationPage)
        self.assertCanNotCreateAt(EditorialListingPage, IndexPage)

    def test_can_add_editorial_child_page(self):
        self.assertCanCreateAt(EditorialListingPage, EditorialPage)
