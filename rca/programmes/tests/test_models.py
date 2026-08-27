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
from rca.programmes.models import (
    ProgrammeIndexPage,
    ProgrammePage,
    ProgrammePageDegreeLevel,
    ProgrammeStudyMode,
)
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


class ProgrammePageDegreeLevelTests(TestCase):
    def setUp(self):
        self.home_page = HomePage.objects.first()
        self.page = ProgrammePageFactory(
            parent=self.home_page, title="Contemporary Art Practice"
        )
        self.ma = DegreeLevelFactory(title="MA")
        self.mfa = DegreeLevelFactory(title="MFA")

    def test_a_page_can_have_multiple_degree_level_entries(self):
        ProgrammePageDegreeLevel.objects.create(
            source_page=self.page, level=self.ma, qs_code=105
        )
        ProgrammePageDegreeLevel.objects.create(
            source_page=self.page, level=self.mfa, qs_code=106
        )

        self.assertEqual(self.page.degree_levels.count(), 2)
        self.assertEqual(
            set(self.page.degree_levels.values_list("level__title", flat=True)),
            {"MA", "MFA"},
        )

    def test_each_degree_level_entry_stores_its_own_details_independently(self):
        ma_entry = ProgrammePageDegreeLevel.objects.create(
            source_page=self.page,
            level=self.ma,
            qs_code=105,
            credits="180",
            time="1 year",
        )
        mfa_entry = ProgrammePageDegreeLevel.objects.create(
            source_page=self.page,
            level=self.mfa,
            qs_code=106,
            credits="360",
            time="2 years",
        )

        # Editing one entry's values must not affect the other's.
        ma_entry.credits = "999"
        ma_entry.save()

        mfa_entry.refresh_from_db()
        self.assertEqual(mfa_entry.credits, "360")
        self.assertEqual(mfa_entry.qs_code, 106)
        self.assertEqual(mfa_entry.time, "2 years")


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
