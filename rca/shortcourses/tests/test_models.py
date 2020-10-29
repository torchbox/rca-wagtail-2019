from django.test import TestCase

from rca.home.models import HomePage
from rca.programmes.models import ProgrammeType
from rca.shortcourses.models import ShortCoursePage


class TestBookingBarLogic(TestCase):
    """ Test the various states that the booking bar logic can return
    Scenarios:
        1 - If no data is passed to the booking bar, E.G no dates data should
        show "Applications are now closed", and an automatic 'register intereset
        link' populated using the AccessPlanit course ID
        2a - Custom/Manual dates have been defined. Booking bar should show
        'Next start date', and a 'book now' (first date item has book now url)
        link from the first manually added date via ShortCourseManualDate
        (manual_bookings)
        2b - Custom/Manual dates have been defined. Booking bar should show
        'Next start date', and a 'register' (first date item has register url)
        link from the first manually added date via ShortCourseManualDate
        (manual_bookings)
        3a - If there is access planit data fetched for the course_id, Booking
        bar should show 'next course starts: start_date' and a book now link
        3b - If there is access planit data fetched for the course_id and the
        short course has an 'application_form_url' defined, Booking bar should
        show 'Next course starts: start date' and  'Submit form to apply' link
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
        )

    def test_no_data_at_all(self):
        """1 - If no data is passed to the booking bar, E.G no dates data
        should show "Applications are now closed", and an automatic 'register
        intereset link' populated using the AccessPlanit course ID"""

        self.home_page.add_child(instance=self.short_course_page)

        # Get the auto register interest link made in the context
        register_link = self.short_course_page.get_context(request=None)[
            "register_interest_link"
        ]

        booking_bar_data = self.short_course_page._format_booking_bar(
            register_interest_link=register_link, access_planit_data=None
        )

        self.assertEqual(
            {
                "message": "Applications are now closed",
                "action": "Register your interest for upcoming dates",
                "link": register_link,
            },
            booking_bar_data,
        )

        response = self.client.get("/short-course/")
        self.assertContains(response, "Short course title")
        self.assertContains(response, "Register your interest for upcoming dates")
        self.assertContains(response, "Applications are now closed")
        self.assertContains(response, "register_links")
        self.assertEqual(response.render().status_code, 200)

    def test_custom_dates_book(self):
        # TODO
        """2a - Custom/Manual dates have been defined. Booking bar should show
        'Next start date', and a 'book now' (first date item has book now url)
        link from the first manually added date via ShortCourseManualDate
        (manual_bookings)"""
        pass

    def test_custom_dates_register(self):
        """2b - Custom/Manual dates have been defined. Booking bar should show
        'Next start date', and a 'register' (first date item has register url)
        link from the first manually added date via ShortCourseManualDate
        (manual_bookings)"""
        pass

    def test_access_planit_book(self):
        """3a - If there is access planit data fetched for the course_id,
        Booking bar should show 'next course starts: start_date' and a
        book now link """
        pass

    def test_access_planit_apply(self):
        """3b - If there is access planit data fetched for the course_id and
        the short course has an 'application_form_url' defined, Booking bar
        should show 'Next course starts: start date' and 'Submit form to
        apply' link"""
        pass
