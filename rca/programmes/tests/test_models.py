from wagtail.images.tests.utils import get_test_image_file
from wagtail.tests.utils import WagtailPageTests

from rca.home.models import HomePage
from rca.images.models import CustomImage
from rca.programmes.factories import ProgrammePageFactory
from rca.programmes.models import ProgrammeIndexPage, ProgrammePage
from rca.standardpages.models import IndexPage, InformationPage


class TestProgrammePageFactories(WagtailPageTests):
    def test_factories(self):
        ProgrammePageFactory()


class ProgrammePageTests(WagtailPageTests):
    def setUp(self):
        self.home_page = HomePage.objects.first()
        self.user = self.login()
        self.image = CustomImage.objects.create(
            title="Test image", file=get_test_image_file(),
        )

    def test_can_create_under_programme_index_page(self):
        self.assertCanCreateAt(ProgrammeIndexPage, ProgrammePage)

    def test_cant_create_under_other_pages(self):
        self.assertCanNotCreateAt(IndexPage, ProgrammePage)
        self.assertCanNotCreateAt(InformationPage, ProgrammePage)
        self.assertCanNotCreateAt(HomePage, ProgrammePage)

    def test_page_count_rules(self):
        # A single programme index should be creatable
        self.assertTrue(ProgrammeIndexPage.can_create_at(self.home_page))
        self.home_page.add_child(
            instance=ProgrammeIndexPage(
                title="programmes",
                slug="programmes",
                introduction="The introduction",
                contact_model_title="Contact us",
                contact_model_image=self.image,
                contact_model_text="Contact us",
                contact_model_url="https://torchbox.com",
            )
        )
        # A second programme index page should not be creatable
        self.assertFalse(ProgrammeIndexPage.can_create_at(self.home_page))
