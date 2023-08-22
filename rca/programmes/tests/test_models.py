from django.test import TestCase
from wagtail.images.tests.utils import get_test_image_file
from wagtail.test.utils import WagtailPageTestCase

from rca.home.models import HomePage
from rca.images.models import CustomImage
from rca.programmes.factories import (
    DegreeLevelFactory,
    ProgrammePageFactory,
    ProgrammeTypeFactory,
)
from rca.programmes.models import ProgrammeIndexPage, ProgrammePage, ProgrammeStudyMode
from rca.standardpages.models import IndexPage, InformationPage


class TestProgrammePageFactories(TestCase):
    def test_factories(self):
        ProgrammePageFactory()
        DegreeLevelFactory()
        ProgrammeTypeFactory()


class ProgrammePageTests(WagtailPageTestCase):
    def setUp(self):
        self.home_page = HomePage.objects.first()
        self.user = self.login()
        self.image = CustomImage.objects.create(
            title="Test image",
            file=get_test_image_file(),
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


class TestProgrammeStudyMode(TestCase):
    def test_cannot_create_more_than_two_instances(self):
        """
        We already have two ProgrammeStudyMode instances created
        as part of a data migration. Attempting to create a third
        should raise a ValueError.
        """
        self.assertEqual(ProgrammeStudyMode.objects.count(), 2)

        with self.assertRaises(ValueError):
            ProgrammeStudyMode.objects.create(title="Online")

        with self.assertRaises(ValueError):
            mode = ProgrammeStudyMode(title="Hybrid")
            mode.save()
