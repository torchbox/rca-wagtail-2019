import datetime
import logging
import warnings
from unittest import mock

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.http.request import QueryDict
from django.test import TestCase
from requests.exceptions import Timeout

from rca.home.models import HomePage
from rca.programmes.models import ProgrammeType
from rca.shortcourses.access_planit import (
    AccessPlanitCourseChecker,
    AccessPlanitException,
    AccessPlanitXML,
    AccessPlanitXMLParser,
)
from rca.shortcourses.models import ShortCoursePage

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", message="No directory at", module="whitenoise.base")


def mocked_fetch_data_from_xml(**kargs):
    with open("./rca/shortcourses/tests/test_data.xml", "r") as file:
        data = AccessPlanitXMLParser(xml=file.read())
        data = data.get_parsed_data()
    return data


def mocked_fetch_valid_course_data(**kargs):
    with open("./rca/shortcourses/tests/valid_course_data.xml", "r") as file:
        data = file.read()
    return data


def mocked_fetch_invalid_course_data(**kargs):
    with open("./rca/shortcourses/tests/invalid_course_data.xml", "r") as file:
        data = file.read()
    return data


class AccessPlanitXMLTest(TestCase):
    def setUp(self):
        ProgrammeType.objects.create(
            display_name="Design", description="Some description text", id=1
        )
        self.expected_data = [
            {
                "course_date_id": "12086",
                "course_id": "731014",
                "cost": "1250",
                "start_date": datetime.datetime(2020, 3, 27, 9, 0),
                "end_date": datetime.datetime(2020, 4, 2, 17, 0),
                "spaces_available": "22",
                "status": "Available",
                "book_now_url": (
                    "https://rca.accessplanit.com/accessplansand"
                    "box/clientinput/course/coursebooker.aspx?coursedateid=12086"
                ),
                "enquire_url": (
                    "https://rca.accessplanit.com/accessplansand"
                    "box/clientinput/company/contactcompany.aspx?contacttype=8"
                    "&coursecalid=12086"
                ),
            },
            {
                "course_date_id": "12085",
                "course_id": "731014",
                "cost": "9000",
                "start_date": datetime.datetime(2020, 5, 13, 9, 0),
                "end_date": datetime.datetime(2020, 5, 19, 17, 0),
                "spaces_available": "22",
                "status": "Available",
                "book_now_url": (
                    "https://rca.accessplanit.com/accessplansand"
                    "box/clientinput/course/coursebooker.aspx?coursedateid=12085"
                ),
                "enquire_url": (
                    "https://rca.accessplanit.com/accessplansand"
                    "box/clientinput/company/contactcompany.aspx?contacttype=8"
                    "&coursecalid=12085"
                ),
            },
            {
                "course_date_id": "12071",
                "course_id": "731014",
                "cost": "1250",
                "start_date": datetime.datetime(2020, 7, 20, 9, 0),
                "end_date": datetime.datetime(2020, 7, 24, 17, 0),
                "spaces_available": "20",
                "status": "Available",
                "book_now_url": (
                    "https://rca.accessplanit.com/accessplansand"
                    "box/clientinput/course/coursebooker.aspx?coursedateid=12071"
                ),
                "enquire_url": (
                    "https://rca.accessplanit.com/accessplansand"
                    "box/clientinput/company/contactcompany.aspx?contacttype=8"
                    "&coursecalid=12071"
                ),
            },
        ]
        query = QueryDict(mutable=True)
        query.update(
            {
                "CompanyID": "ROYALC9RCH",
                "courseIDs": 1,
                "venueIDs": "",
                "categoryIDs": "",
            }
        )
        self.query = query.urlencode()

    def test_xml_fetch(self):
        """ Test the XML fetch responds. """
        with self.settings(
            ACCESS_PLANIT_XML_BASE_URL="https://rca.accessplanit.com/accessplansandbox/services/WebIntegration.asmx/"
            "GetCoursesPackage?"
        ):
            response = requests.get(
                settings.ACCESS_PLANIT_XML_BASE_URL + self.query, timeout=5
            )
            self.assertEqual(response.status_code, 200)

    def test_xml_fetch_no_venue(self):
        """ Prove that you must pass blank values as parameters"""
        with self.settings(
            ACCESS_PLANIT_XML_BASE_URL="https://rca.accessplanit.com/accessplansandbox/services/WebIntegration.asmx/"
            "GetCoursesPackage?"
        ):
            query = QueryDict(mutable=True)
            query.update({"CompanyID": "ROYALC9RCH", "courseIDs": 1})
            query = query.urlencode()
            response = requests.get(
                settings.ACCESS_PLANIT_XML_BASE_URL + query, timeout=5
            )
            self.assertEqual(response.text, """Missing parameter: venueIDs.\r\n""")
            self.assertEqual(response.status_code, 500)

    """ Patch the request module totally to force the timeout so we can test the
        result of the try/expect.

        Test here that data returned from a timeout is None
    """

    @mock.patch("rca.shortcourses.access_planit.requests.get")
    def test_data_if_timeout(self, mock_get):
        """ If a timeout is caught the xml_data should be None"""
        logging.disable(logging.CRITICAL)
        mock_get.side_effect = Timeout
        data = AccessPlanitXML(course_id=1)
        xml_data = data.get_data()
        self.assertEqual(xml_data, None)

    @mock.patch(
        "rca.shortcourses.access_planit.AccessPlanitXML.fetch_data_from_xml",
        side_effect=mocked_fetch_data_from_xml,
    )
    @mock.patch("rca.shortcourses.access_planit.requests.get")
    @mock.patch(
        "rca.shortcourses.access_planit.AccessPlanitCourseChecker.course_exists",
        mock.Mock(return_value=True),
    )
    def test_cached_data_if_timeout(self, mock_get, mocked_fetch_data_from_xml):
        """ Test getting stale cache data with a Timeout failure to get data"""
        logging.disable(logging.CRITICAL)
        ShortCoursePage.objects.create(
            title=f"Short course 1",
            path="1",
            depth="001",
            access_planit_course_id=1,
            programme_type_id=1,
            contact_url="https://rca.ac.uk",
            contact_text="Read more",
            hero_colour_option=1,
        )
        # Generate the mocked xml data
        AccessPlanitXML(course_id=1).get_data()
        cache_key = f"short_course_1"
        self.assertEqual(cache.get(cache_key), self.expected_data)
        # Add a timeout for the new data request
        mock_get.side_effect = Timeout
        AccessPlanitXML(course_id=1).get_data()

        # Now check the stale cache data is there
        self.assertEqual(cache.get(cache_key), self.expected_data)

    def test_required_course_id(self):
        """ The access_planit_course_id is a required field, however if access_planit_course_id
        is made non-required we want some tests to fail, as it will have unwanted effects,
        the validation on the model should be able to cast the course value to an integer"""

        with self.assertRaises(TypeError):
            ShortCoursePage.objects.create(
                title=f"Short course should not save", path=100, depth="001"
            )
        with self.assertRaises(TypeError):
            ShortCoursePage.objects.create(
                title=f"Short course should not save",
                path=100,
                depth="001",
                access_planit_course_id="course id cannot be a string",
                programme_type_id=1,
                contact_url="https://rca.ac.uk",
                contact_text="Read more",
                hero_colour_option=1,
            )

    def test_cache_data_for_non_valid_course_id(self):
        """ Technically, you can add any integer as a course ID and some will
        not fetch data"""
        data = AccessPlanitXML(course_id=1).get_data()
        self.assertEqual(data, None)

    @mock.patch(
        "rca.shortcourses.access_planit.AccessPlanitXML.fetch_data_from_xml",
        side_effect=mocked_fetch_data_from_xml,
    )
    @mock.patch(
        "rca.shortcourses.access_planit.AccessPlanitCourseChecker.course_exists",
        mock.Mock(return_value=True),
    )
    def test_management_command_fetch_with_example_data(
        self, mocked_fetch_data_from_xml
    ):
        """ Test that the example xml goes in the cache as expected """
        for i in range(1, 5):
            ShortCoursePage.objects.create(
                title=f"Short course {i}",
                path=str(i),
                depth="001",
                access_planit_course_id=i,
                programme_type_id=1,
                contact_url="https://rca.ac.uk",
                contact_text="Read more",
                hero_colour_option=1,
                show_register_link=0,
            )
        call_command("fetch_access_planit_data")
        for i in range(1, 5):
            cache_key = f"short_course_{i}"
            self.assertEqual(cache.get(cache_key), self.expected_data)

    @mock.patch("rca.shortcourses.access_planit.requests.get")
    @mock.patch(
        "rca.shortcourses.access_planit.AccessPlanitCourseChecker.course_exists",
        mock.Mock(return_value=True),
    )
    def test_page_renders_with_timeout(self, mock_get):
        logging.disable(logging.CRITICAL)
        """ If there is a timeout for the xml request when the page loads,
        ensure the page still renders with the empty data"""
        home_page = HomePage.objects.first()
        mock_get.side_effect = Timeout
        short_course_page = ShortCoursePage(
            title="Short course title",
            slug="short-course",
            access_planit_course_id="1",
            programme_type_id=1,
            contact_url="https://rca.ac.uk",
            contact_text="Read more",
            hero_colour_option=1,
        )
        home_page.add_child(instance=short_course_page)
        response = self.client.get("/short-course/")
        self.assertTemplateUsed(
            response, "patterns/pages/shortcourses/short_course.html"
        )
        self.assertContains(response, "Short course title")
        self.assertEqual(response.render().status_code, 200)

    @mock.patch(
        "rca.shortcourses.access_planit.AccessPlanitXML.fetch_data_from_xml",
        side_effect=mocked_fetch_data_from_xml,
    )
    @mock.patch(
        "rca.shortcourses.access_planit.AccessPlanitCourseChecker.course_exists",
        mock.Mock(return_value=True),
    )
    def test_page_renders_good_xml(self, mocked_fetch_data_from_xml):
        """ Test that the example xml file is passed through the parser and is set
        in cache, and when retrieved is what we expect """
        home_page = HomePage.objects.first()
        short_course_page = ShortCoursePage(
            title="Short course title",
            slug="short-course",
            access_planit_course_id="1",
            programme_type_id=1,
            contact_url="https://rca.ac.uk",
            contact_text="Read more",
            hero_colour_option=1,
        )
        home_page.add_child(instance=short_course_page)
        response = self.client.get("/short-course/")

        self.assertTemplateUsed(
            response, "patterns/pages/shortcourses/short_course.html"
        )
        self.assertContains(response, "Short course title")
        self.assertEqual(response.render().status_code, 200)
        self.assertEqual(cache.get("short_course_1"), self.expected_data)

    def test_parsing(self):
        with open("./rca/shortcourses/tests/test_data.xml", "r") as file:
            data = file.read()
            parser = AccessPlanitXMLParser(xml=data)
            parsed_data = parser.get_parsed_data()
            self.assertEqual(parsed_data, self.expected_data)


class AccessPlanitCourseCheckerTest(TestCase):
    def setUp(self):
        ProgrammeType.objects.create(
            display_name="Design", description="Some description text", id=1
        )
        query = QueryDict(mutable=True)
        query.update(
            {
                "CompanyID": "ROYALC9RCH",
                "courseIDs": 1,
                "venueIDs": "",
                "categoryIDs": "",
            }
        )
        self.query = query.urlencode()

    def test_xml_fetch(self):
        """ Test the XML fetch responds. """
        with self.settings(
            ACCESS_PLANIT_XML_COURSE_URL="https://rca.accessplanit.com/accessplansandbox/services/WebIntegration.asmx/"
            "GetCourses?"
        ):
            response = requests.get(
                settings.ACCESS_PLANIT_XML_COURSE_URL + self.query, timeout=5
            )
            self.assertEqual(response.status_code, 200)

    """ Patch the request module totally to force the timeout so we can test the
        result of the try/expect.
    """

    @mock.patch("rca.shortcourses.access_planit.requests.get")
    def test_exception_if_timeout(self, mock_get):
        """ If a timeout is caught then throw an exception that's handled as a validation error"""
        logging.disable(logging.CRITICAL)
        mock_get.side_effect = Timeout

        # Checker throws the expected exception on timeout
        data = AccessPlanitCourseChecker(course_id=1)
        with self.assertRaises(AccessPlanitException):
            data.fetch_course_data()

        # Model form throws a validation error on timeout
        with self.assertRaises(ValidationError):
            ShortCoursePage.objects.create(
                title=f"Short course 1",
                path="1",
                depth="001",
                access_planit_course_id=1,
                programme_type_id=1,
                contact_url="https://rca.ac.uk",
                contact_text="Read more",
                hero_colour_option=1,
            )

    @mock.patch(
        "rca.shortcourses.access_planit.AccessPlanitCourseChecker.fetch_course_data",
        side_effect=mocked_fetch_valid_course_data,
    )
    def test_page_accepts_valid_course(self, mocked_fetch_valid_course_data):
        # No error should be thrown by this call
        ShortCoursePage.objects.create(
            title=f"Short course 1",
            path="1",
            depth="001",
            access_planit_course_id=1,
            programme_type_id=1,
            contact_url="https://rca.ac.uk",
            contact_text="Read more",
            hero_colour_option=1,
        )

    @mock.patch(
        "rca.shortcourses.access_planit.AccessPlanitCourseChecker.fetch_course_data",
        side_effect=mocked_fetch_invalid_course_data,
    )
    def test_page_rejects_invalid_couse(self, mocked_fetch_invalid_course_data):
        with self.assertRaises(ValidationError):
            ShortCoursePage.objects.create(
                title=f"Short course 1",
                path="1",
                depth="001",
                access_planit_course_id=1,
                programme_type_id=1,
                contact_url="https://rca.ac.uk",
                contact_text="Read more",
                hero_colour_option=1,
            )
