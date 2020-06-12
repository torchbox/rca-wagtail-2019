import logging
from unittest.mock import patch

from django.test import TestCase
from requests.exceptions import Timeout

from rca.api_content.content import CantPullFromRcaApi, pull_related_students
from rca.home.models import HomePage
from rca.people.models import StaffPage


def mocked_student_image():
    return {
        "thumbnail": {"url": "https://foo.com/profile.png", "width": 165, "height": 135}
    }


def mocked_fetch_students():
    return {
        "supervised_students": [
            {
                "status": "Current",
                "link": "https://foo.com/link-to-profile",
                "name": "Fox Mulder",
            }
        ]
    }


def mocked_fetch_students_with_image():
    return {
        "supervised_students": [
            {
                "status": "Current",
                "link": "https://foo.com/link-to-profile",
                "name": "Fox Mulder",
                "image": 1,
            }
        ]
    }


class FetchRelatedStudentsTest(TestCase):
    def setUp(self):
        super().setUp()

    @patch(
        "rca.api_content.content.fetch_data",
        return_value=mocked_fetch_students_with_image(),
    )
    @patch(
        "rca.api_content.content.fetch_student_image",
        return_value=mocked_student_image(),
    )
    def test_parsing_with_image(self, mocked_fetch_students, mocked_student_image):
        results = pull_related_students(1)
        self.assertEqual(
            results,
            [
                {
                    "status": "Current",
                    "link": "https://foo.com/link-to-profile",
                    "name": "Fox Mulder",
                    "image": 1,
                    "image_url": {
                        "thumbnail": {
                            "url": "https://foo.com/profile.png",
                            "width": 165,
                            "height": 135,
                        }
                    },
                }
            ],
        )

    @patch("rca.api_content.content.fetch_data", return_value=mocked_fetch_students())
    def test_parsing_with_no_image(self, mocked_fetch_students):
        results = pull_related_students(1)
        self.assertEqual(
            results,
            [
                {
                    "status": "Current",
                    "link": "https://foo.com/link-to-profile",
                    "name": "Fox Mulder",
                }
            ],
        )

    # What happens with a Timeout?
    @patch("rca.api_content.content.requests.get")
    def test_timeout_raises_cannot_pull_from_rca(self, mock_get):
        logging.disable(logging.CRITICAL)
        with self.assertRaises(CantPullFromRcaApi):
            mock_get.side_effect = Timeout
            results = pull_related_students(1)  # noqa

    # Test rendering a staff page with a bad staff ID
    def test_staff_page(self):
        home_page = HomePage.objects.first()
        staff_page = StaffPage(
            title="Jane Doe",
            first_name="Jane",
            last_name="Doe",
            path="1",
            depth="001",
            legacy_staff_id=1,
            slug="jane-doe",
        )
        home_page.add_child(instance=staff_page)
        response = self.client.get("/jane-doe/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "patterns/pages/staff/staff_detail.html")
        self.assertContains(response, "Jane Doe")

    # Test rendering a staff page with a bad staff ID and a Timeout
    @patch("rca.api_content.content.requests.get")
    def test_staff_page_api_timeout(self, mock_get):
        mock_get.side_effect = Timeout
        home_page = HomePage.objects.first()
        staff_page = StaffPage(
            title="Jane Doe",
            first_name="Jane",
            last_name="Doe",
            path="1",
            depth="001",
            legacy_staff_id=1,
            slug="jane-doe",
        )
        home_page.add_child(instance=staff_page)
        response = self.client.get("/jane-doe/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "patterns/pages/staff/staff_detail.html")
        self.assertContains(response, "Jane Doe")
