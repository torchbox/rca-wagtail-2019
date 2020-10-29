from django.test import TestCase

from rca.home.models import HomePage
from rca.programmes.models import ProgrammeType
from rca.shortcourses.models import ShortCoursePage


class TestBookingBarLogic(TestCase):
    """ Test the various states that the booking bar logic can return
    Scenarios:
        1 - no data at all show applications are closed
        2 - If no booking data and show_register_link checked and AP id is preset
            - populate auto register links in sidebar and in booking bar
        3 - if no booking data and show_register_link checked and AP id is preset
            and manual_register_url is defined: Show 'register interest' in booking bar
            using manual_register_url.value
        4 - if access planit data comes through register interest link
            in the modal and sidebar automatically goes to AP form url. Booking
            bar will show next start date and 'book' link to open modal.
        5 - if access planit data comes through AND page.manual_register_url
            is defined, modal and sidebar links go to page.manual_register_url.
            Booking bar will show next start date and 'book' link to open modal.
        6 - if access planit data comes through, but a page.application_form_url
            is defined, booking bar shows next AP course date and "Submit for to
            apply". > opens modal, modal shows 'apply' links in place of book.
        7 - If manual booking dates are defined. The first/top booking date is
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
        )

    def test_no_data(self):
        """
        1 no data at all show applications are closed
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
        self.assertContains(response, register_link)
        self.assertEqual(response.render().status_code, 200)

    def test_no_data_at_and_register_link(self):
        """
        2 If no booking data and show_register_link checked and AP id is preset
        populate auto register links in sidebar and in booking bar
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
        self.assertContains(response, register_link)
        self.assertEqual(response.render().status_code, 200)

    def test_custom_dates_register(self):
        """
        3 if not booking data and show_register_link checked and AP id is preset
        and manual_register_url is defined: Show 'register interest' in booking bar
        using manual_register_url.value
        """
        pass

    def test_access_planit_book(self):
        """
        4 if access planit data comes through register interest link
        in the modal and sidebar automatically goes to AP form url. Booking
        bar will show next start date and 'book' link to open modal.
        """
        pass

    def test_access_planit_apply_manual_register(self):
        """
        5 if access planit data comes through AND page.manual_register_url
        is defined, modal and sidebar links go to page.manual_register_url.
        Booking bar will show next start date and 'book' link to open modal
        """
        pass

    def test_access_planit_apply(self):
        """
        6 if access planit data comes through, but a page.application_form_url
        is defined, booking bar shows next AP course date and "Submit for to
        apply". > opens modal, modal shows 'apply' links in place of book
        """
        pass

    def test_manual_dates(self):
        """
        7 If manual booking dates are defined. The first/top booking date is
        shown in the booking bar, 'Book' link in the booking bar opens modal
        to show booking manually added booking items
        """
