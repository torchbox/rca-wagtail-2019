from django.test import TestCase

from rca.home.models import HomePage
from rca.programmes.factories import DegreeLevelFactory, ProgrammePageFactory
from rca.programmes.models import ProgrammeStudyMode, ProgrammeStudyModeProgrammePage


class ProgrammesAPIResponseTest(TestCase):
    def setUp(self):
        self.home_page = HomePage.objects.first()

        self.full_time_study_mode = ProgrammeStudyMode.objects.get(
            title="Full-time study"
        )
        self.part_time_study_mode = ProgrammeStudyMode.objects.get(
            title="Part-time study"
        )

        self.programme_page_title = "Print"
        self.degree_level_title = "MA"

        degree_level = DegreeLevelFactory(title=self.degree_level_title)
        self.programme_page = ProgrammePageFactory(
            parent=self.home_page,
            title=self.programme_page_title,
            degree_level=degree_level,
        )

        self.base_url = (
            "/api/v3/pages/?type=programmes.ProgrammePage"
            "&limit=50&fields=summary%2Chero_image_square"
        )

    def test_should_return_if_querying_title_and_degree_level(self):
        ProgrammeStudyModeProgrammePage.objects.create(
            page=self.programme_page, programme_study_mode=self.full_time_study_mode
        )

        # Check by just using the title of the page.
        response = self.client.get(
            f"{self.base_url}&full-time=true"
            f"&part-time=true&search={self.programme_page_title}"
        )
        data = response.json()

        self.assertEqual(data["meta"]["total_count"], 1)
        self.assertEqual(data["items"][0]["id"], self.programme_page.id)

        # Check by using the page and degree name.
        response = self.client.get(
            f"{self.base_url}&full-time=true"
            f"&part-time=true&search={self.programme_page_title}+{self.degree_level_title}"
        )
        data = response.json()

        self.assertEqual(data["meta"]["total_count"], 1)
        self.assertEqual(data["items"][0]["id"], self.programme_page.id)

    def test_should_not_return_full_time_programmes_if_full_time_is_false(self):
        ProgrammeStudyModeProgrammePage.objects.create(
            page=self.programme_page, programme_study_mode=self.full_time_study_mode
        )

        # Set full-time to true first.
        response = self.client.get(
            f"{self.base_url}&full-time=true"
            f"&part-time=true&search={self.programme_page_title}"
        )
        data = response.json()

        self.assertEqual(data["meta"]["total_count"], 1)
        self.assertEqual(data["items"][0]["id"], self.programme_page.id)

        # Then set it to false - there should be no results now.
        response = self.client.get(
            f"{self.base_url}&full-time=false"
            f"&part-time=true&search={self.programme_page_title}"
        )
        data = response.json()

        self.assertEqual(data["meta"]["total_count"], 0)

    def test_should_not_return_part_time_programmes_if_part_time_is_false(self):
        ProgrammeStudyModeProgrammePage.objects.create(
            page=self.programme_page, programme_study_mode=self.part_time_study_mode
        )

        # Set part-time to true first.
        response = self.client.get(
            f"{self.base_url}&full-time=true"
            f"&part-time=true&search={self.programme_page_title}"
        )
        data = response.json()

        self.assertEqual(data["meta"]["total_count"], 1)
        self.assertEqual(data["items"][0]["id"], self.programme_page.id)

        # Then set it to false - there should be no results now.
        response = self.client.get(
            f"{self.base_url}&full-time=true"
            f"&part-time=false&search={self.programme_page_title}+{self.degree_level_title}"
        )
        data = response.json()

        self.assertEqual(data["meta"]["total_count"], 0)
