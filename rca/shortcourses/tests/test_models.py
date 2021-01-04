import datetime
from unittest import mock

from django.test import TestCase

from rca.home.models import HomePage
from rca.programmes.models import ProgrammeType
from rca.shortcourses.models import ShortCourseManualDate, ShortCoursePage

from .test_access_planit import mocked_fetch_data_from_xml

APPLY_MESSAGE = "Applications are now closed"
APPLY_ACTION = "Register your interest for upcoming dates"


class TestBookingBarLogic(TestCase):
    """ Test the various states that the booking bar logic can return, the logic
    for this has become quite involved so the main aim of the testing here is
    to describe how it acutall functions.

    Scenarios:
        1 - no data at all show applications are closed
            - no page.show_register_link
            - no manual dates
            - no data from access planit
        2 - If no booking data and show_register_link checked and AP id is present
            - populate auto register links in sidebar and in booking bar
        3 - If no booking data and show_register_link checked and AP id is present
            and the manual_registration_url is defined populate manual register
            links in sidebar and in booking bar
        4 - If access planit course data comes through, but a page
            application_form_url is defined, booking bar shows next AP course
            date and "Submit for to apply". The line items in the modal should
            use and show "apply" links in place of book links
        5 - If manual booking dates are defined. The first/top booking date is
            shown in the booking bar, 'Book' link in the booking bar opens modal
            to show booking manually added booking items
    """

    def setUp(self):
        ProgrammeType.objects.create(
            display_name="Design", description="Some description text", id=1
        )
        self.home_page = HomePage.objects.first()
        self.short_course_page = ShortCoursePage(
            title="Short course title",
            slug="short-course",
            access_planit_course_id="1",
            programme_type_id=1,
            contact_url="https://rca.ac.uk",
            contact_text="Read more",
            hero_colour_option=1,
            show_register_link=0,
        )

    @mock.patch(
        "rca.shortcourses.access_planit.AccessPlanitCourseChecker.course_exists",
        mock.Mock(return_value=True),
    )
    def test_no_data(self):
        """
        1 no data at all show applications are closed
            - no page.show_register_link
            - no manual dates
            - no data from access planit
        """
        self.home_page.add_child(instance=self.short_course_page)

        # Get the auto register interest link made in the context
        register_link = self.short_course_page.get_context(request=None)[
            "register_interest_link"
        ]

        booking_bar_data = self.short_course_page._format_booking_bar(
            register_interest_link=register_link, access_planit_data=None
        )

        self.assertEqual(
            {"message": APPLY_MESSAGE, "action": APPLY_ACTION, "link": register_link},
            booking_bar_data,
        )

        response = self.client.get("/short-course/")
        self.assertContains(response, "Short course title")
        self.assertNotIn("Register your interest for upcoming dates", response)
        self.assertContains(response, "Applications are now closed")
        self.assertNotIn(register_link, response)
        self.assertEqual(response.render().status_code, 200)

    @mock.patch(
        "rca.shortcourses.access_planit.AccessPlanitCourseChecker.course_exists",
        mock.Mock(return_value=True),
    )
    def test_no_booking_data_and_register_link(self):
        """
        2 If no booking data and show_register_link checked and AP id is present
        populate automatic register links in sidebar and in booking bar
        """
        self.short_course_page.show_register_link = 1
        self.home_page.add_child(instance=self.short_course_page)

        # Get the auto register interest link made in the context
        # E.G /short-courses/register-your-interest/?course_id=[course_id]

        register_link = self.short_course_page.get_context(request=None)[
            "register_interest_link"
        ]

        booking_bar_data = self.short_course_page._format_booking_bar(
            register_interest_link=register_link, access_planit_data=None
        )

        self.assertEqual(
            {"message": APPLY_MESSAGE, "action": APPLY_ACTION, "link": register_link},
            booking_bar_data,
        )

        response = self.client.get("/short-course/")
        self.assertEqual(
            "https://rca.ac.uk/short-courses/register-your-interest/?course_id=1",
            register_link,
        )
        self.assertContains(response, "Register your interest for upcoming dates")
        self.assertContains(response, "Applications are now closed")
        self.assertContains(response, register_link)
        self.assertEqual(response.render().status_code, 200)

    @mock.patch(
        "rca.shortcourses.access_planit.AccessPlanitCourseChecker.course_exists",
        mock.Mock(return_value=True),
    )
    def test_no_data_and_manual_register_link(self):
        """
        3 If no booking data and show_register_link checked and AP id is present
        and the manual_registration_url is defined
        populate manual register links in sidebar and in booking bar
        """

        self.short_course_page.show_register_link = 1
        manual_registration_url = "https://tochbox.com"
        self.short_course_page.manual_registration_url = manual_registration_url
        self.home_page.add_child(instance=self.short_course_page)

        # Get the auto register interest link made in the context
        # E.G /short-courses/register-your-interest/?course_id=[course_id]
        register_link = self.short_course_page.get_context(request=None)[
            "register_interest_link"
        ]

        booking_bar_data = self.short_course_page._format_booking_bar(
            register_interest_link=register_link, access_planit_data=None
        )
        # Check the manual link has come through as the register link in the booking bar formatter
        self.assertEqual(
            {
                "message": APPLY_MESSAGE,
                "action": APPLY_ACTION,
                "link": manual_registration_url,
            },
            booking_bar_data,
        )

        response = self.client.get("/short-course/")
        self.assertContains(response, "Register your interest for upcoming dates")
        self.assertContains(response, "Applications are now closed")
        self.assertContains(response, manual_registration_url)
        self.assertEqual(response.render().status_code, 200)

    @mock.patch(
        "rca.shortcourses.access_planit.AccessPlanitXML.fetch_data_from_xml",
        side_effect=mocked_fetch_data_from_xml,
    )
    @mock.patch(
        "rca.shortcourses.access_planit.AccessPlanitCourseChecker.course_exists",
        mock.Mock(return_value=True),
    )
    def test_access_planit_apply(self, mocked_fetch_data_from_xml):
        """
        4 If access planit course data comes through, but a page.application_form_url
        is defined, booking bar shows next AP course date and "Submit for to apply".
        The line items in the modal should use and show "apply" links in place
        of book links
        """
        self.short_course_page.application_form_url = "https://applyhere.com"
        self.home_page.add_child(instance=self.short_course_page)
        response = self.client.get("/short-course/")

        self.assertContains(response, "Short course title")
        # The modal booking item
        self.assertContains(
            response,
            '<a href="https://applyhere.com" class="link link--tertiary link--link link--external" target="_blank">',
        )
        self.assertNotIn("Book", response)
        self.assertEqual(response.render().status_code, 200)

    @mock.patch(
        "rca.shortcourses.access_planit.AccessPlanitCourseChecker.course_exists",
        mock.Mock(return_value=True),
    )
    def test_manual_dates(self):
        """
        5 If manual booking dates are defined. The first/top booking date is
        shown in the booking bar, 'Book' link in the booking bar opens modal
        to show booking manually added booking items
        """
        self.short_course_page.manual_bookings = [
            ShortCourseManualDate(
                source_page=self.short_course_page,
                start_date=datetime.date(2020, 10, 1),
                end_date=datetime.date(2020, 10, 3),
                cost=100,
                booking_link="https://bookthiscourse.com",
                sort_order=0,
            ),
            ShortCourseManualDate(
                source_page=self.short_course_page,
                start_date=datetime.date(2020, 10, 20),
                end_date=datetime.date(2020, 10, 30),
                cost=600,
                booking_link="https://bookthisothercourse.com",
                sort_order=1,
            ),
        ]
        self.home_page.add_child(instance=self.short_course_page)
        response = self.client.get("/short-course/")
        self.assertContains(
            response,
            f"Book from \xA3{self.short_course_page.manual_bookings.first().cost}",
        )
        self.assertContains(response, "Next course starts 01 October 2020")
        self.assertEqual(response.render().status_code, 200)
