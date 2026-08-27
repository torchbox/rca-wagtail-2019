from django.test import TestCase

from rca.home.models import HomePage
from rca.programmes.factories import DegreeLevelFactory, ProgrammePageFactory
from rca.programmes.models import (
    ProgrammePageDegreeLevel,
    ProgrammeStudyMode,
    ProgrammeStudyModeProgrammePage,
)


def add_full_and_part_time_study_modes(page):
    for title in ("Full-time study", "Part-time study"):
        ProgrammeStudyModeProgrammePage.objects.create(
            page=page, programme_study_mode=ProgrammeStudyMode.objects.get(title=title)
        )


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

    def test_should_exclude_flagged_programme_from_listing(self):
        self.programme_page.exclude_from_programme_finder = True
        self.programme_page.save()

        response = self.client.get(self.base_url)
        data = response.json()

        self.assertEqual(data["meta"]["total_count"], 0)

    def test_should_exclude_flagged_programme_from_text_search(self):
        self.programme_page.exclude_from_programme_finder = True
        self.programme_page.save()

        response = self.client.get(
            f"{self.base_url}&search={self.programme_page_title}"
        )
        data = response.json()

        self.assertEqual(data["meta"]["total_count"], 0)


class DegreeLevelFilterTest(TestCase):
    def setUp(self):
        self.home_page = HomePage.objects.first()

        self.ma = DegreeLevelFactory(title="MA")
        self.mfa = DegreeLevelFactory(title="MFA")

        self.ma_page = ProgrammePageFactory(
            parent=self.home_page, title="Contemporary Art Practice MA"
        )
        ProgrammePageDegreeLevel.objects.create(
            source_page=self.ma_page, level=self.ma, qs_code=105
        )
        add_full_and_part_time_study_modes(self.ma_page)

        self.mfa_page = ProgrammePageFactory(
            parent=self.home_page, title="Contemporary Art Practice MFA"
        )
        ProgrammePageDegreeLevel.objects.create(
            source_page=self.mfa_page, level=self.mfa, qs_code=106
        )
        add_full_and_part_time_study_modes(self.mfa_page)

        self.base_url = (
            "/api/v3/pages/?type=programmes.ProgrammePage"
            "&limit=50&fields=summary%2Chero_image_square"
            "&full-time=true&part-time=true"
        )

    def test_filters_pages_by_a_single_degree_level(self):
        response = self.client.get(f"{self.base_url}&degree_levels={self.ma.pk}")
        data = response.json()

        self.assertEqual(data["meta"]["total_count"], 1)
        self.assertEqual(data["items"][0]["id"], self.ma_page.id)

    def test_filters_pages_by_multiple_degree_levels(self):
        response = self.client.get(
            f"{self.base_url}&degree_levels={self.ma.pk}&degree_levels={self.mfa.pk}"
        )
        data = response.json()

        self.assertEqual(data["meta"]["total_count"], 2)
        returned_ids = {item["id"] for item in data["items"]}
        self.assertEqual(returned_ids, {self.ma_page.id, self.mfa_page.id})

    def test_returns_all_programmes_when_no_degree_level_given(self):
        response = self.client.get(self.base_url)
        data = response.json()

        self.assertEqual(data["meta"]["total_count"], 2)

    def _create_multi_award_page(self):
        # A single Programme page carrying both an MA and an MFA entry,
        # mirroring the "Contemporary Art Practice" example from R1-365.
        page = ProgrammePageFactory(
            parent=self.home_page, title="Contemporary Art Practice"
        )
        ProgrammePageDegreeLevel.objects.create(
            source_page=page, level=self.ma, qs_code=201, credits="180", time="1 year"
        )
        ProgrammePageDegreeLevel.objects.create(
            source_page=page, level=self.mfa, qs_code=202, credits="360", time="2 years"
        )
        add_full_and_part_time_study_modes(page)
        return page

    def test_multi_award_page_is_returned_under_each_of_its_degree_levels(self):
        multi_award_page = self._create_multi_award_page()

        response_ma = self.client.get(f"{self.base_url}&degree_levels={self.ma.pk}")
        response_mfa = self.client.get(f"{self.base_url}&degree_levels={self.mfa.pk}")

        self.assertIn(
            multi_award_page.id,
            {item["id"] for item in response_ma.json()["items"]},
        )
        self.assertIn(
            multi_award_page.id,
            {item["id"] for item in response_mfa.json()["items"]},
        )

    def test_multi_award_page_is_not_duplicated_in_results(self):
        multi_award_page = self._create_multi_award_page()

        # An unfiltered listing should show it once, not once per degree level.
        response = self.client.get(self.base_url)
        matching_items = [
            item
            for item in response.json()["items"]
            if item["id"] == multi_award_page.id
        ]
        self.assertEqual(len(matching_items), 1)

        # Filtering by both of its degree levels together should still only
        # return it once.
        response = self.client.get(
            f"{self.base_url}&degree_levels={self.ma.pk}&degree_levels={self.mfa.pk}"
        )
        matching_items = [
            item
            for item in response.json()["items"]
            if item["id"] == multi_award_page.id
        ]
        self.assertEqual(len(matching_items), 1)
