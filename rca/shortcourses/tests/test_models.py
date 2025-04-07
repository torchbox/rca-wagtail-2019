import datetime

from django.test import TestCase

from rca.home.models import HomePage
from rca.programmes.models import ProgrammeType
from rca.shortcourses.models import ShortCourseManualDate, ShortCoursePage

from ..factories import ShortCoursePageFactory

APPLY_MESSAGE = "Bookings not yet open"
APPLY_ACTION = "Register your interest for upcoming dates"


class TestShortCoursePageFactories(TestCase):
    def test_factories(self):
        ShortCoursePageFactory()


class TestBookingBarLogic(TestCase):
    """Test the various states that the booking bar logic can return, the logic
    for this has become quite involved so the main aim of the testing here is
    to describe how it actually functions.

    Scenarios:
        1 - no data at all show applications are closed
            - no page.show_register_link
            - no manual dates
        2 - If no booking data and show_register_link checked
            - populate auto register links in sidebar and in booking bar
        3 - If no booking data and show_register_link checked
            and the manual_registration_url is defined populate manual register
            links in sidebar and in booking bar
        4 - If manual booking dates are defined. The first/top booking date is
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
            contact_model_url="https://rca.ac.uk",
            contact_model_text="Read more",
            show_register_link=0,
        )

    def test_no_data(self):
        """
        1 no data at all show applications are closed
            - no page.show_register_link
            - no manual dates
        """
        self.home_page.add_child(instance=self.short_course_page)

        # Get the auto register interest link made in the context
        register_link = self.short_course_page.get_context(request=None)[
            "register_interest_link"
        ]

        booking_bar_data = self.short_course_page._format_booking_bar()

        self.assertEqual(
            {"message": APPLY_MESSAGE, "action": APPLY_ACTION, "link": register_link},
            booking_bar_data,
        )

        response = self.client.get("/short-course/")
        self.assertContains(response, "Short course title")
        self.assertNotIn("Register your interest for upcoming dates", response)
        self.assertContains(response, APPLY_MESSAGE)
        self.assertNotIn(register_link, response)
        self.assertEqual(response.render().status_code, 200)

    def test_no_booking_data_and_register_link(self):
        """
        2 If no booking data and show_register_link checked populate automatic
        register links in sidebar and in booking bar
        """
        self.short_course_page.show_register_link = 1
        manual_registration_url = (
            "https://rca.ac.uk/short-courses/register-your-interest/"
        )
        self.short_course_page.manual_registration_url = manual_registration_url
        self.home_page.add_child(instance=self.short_course_page)

        # Get the auto register interest link made in the context
        # E.G /short-courses/register-your-interest/?course_id=[course_id]

        register_link = self.short_course_page.get_context(request=None)[
            "register_interest_link"
        ]

        booking_bar_data = self.short_course_page._format_booking_bar()

        self.assertEqual(
            {"message": APPLY_MESSAGE, "action": APPLY_ACTION, "link": register_link},
            booking_bar_data,
        )

        response = self.client.get("/short-course/")
        self.assertEqual(
            "https://rca.ac.uk/short-courses/register-your-interest/",
            register_link,
        )
        self.assertContains(response, "Register your interest for upcoming dates")
        self.assertContains(response, APPLY_MESSAGE)
        self.assertContains(response, register_link)
        self.assertEqual(response.render().status_code, 200)

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

        booking_bar_data = self.short_course_page._format_booking_bar()
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
        self.assertContains(response, APPLY_MESSAGE)
        self.assertContains(response, manual_registration_url)
        self.assertEqual(response.render().status_code, 200)

    def test_manual_dates(self):
        """
        4 If manual booking dates are defined. The first/top booking date is
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
            f"Book from \xa3{self.short_course_page.manual_bookings.first().cost}",
        )
        self.assertContains(response, "Next course starts 1 October 2020")

        self.assertEqual(response.render().status_code, 200)
