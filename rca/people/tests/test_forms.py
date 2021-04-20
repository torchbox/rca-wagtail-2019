from django.test import TestCase
from wagtail.tests.utils.form_data import nested_form_data

from rca.people.factories import StudentPageFactory
from rca.people.models import StudentPage
from rca.users.factories import UserFactory


class TestStudentPageAdminForm(TestCase):
    def setUp(self):
        self.student_page = StudentPageFactory()
        self.form_class = StudentPage.get_edit_handler().get_form_class()
        self.student = UserFactory()

    def get_form_data(self):
        return nested_form_data(
            {
                "title": "Monty Python",
                "first_name": "Monty",
                "last_name": "Python",
                "related_supervisor-TOTAL_FORMS": "0",
                "related_supervisor-INITIAL_FORMS": "0",
                "related_supervisor-MIN_NUM_FORMS": "0",
                "related_supervisor-MAX_NUM_FORMS": "1000",
                "related_project_pages-TOTAL_FORMS": "0",
                "related_project_pages-INITIAL_FORMS": "0",
                "related_project_pages-MIN_NUM_FORMS": "0",
                "related_project_pages-MAX_NUM_FORMS": "5",
                "gallery_slides-TOTAL_FORMS": "0",
                "gallery_slides-INITIAL_FORMS": "0",
                "gallery_slides-MIN_NUM_FORMS": "0",
                "gallery_slides-MAX_NUM_FORMS": "5",
                "additional_information_title": "",
                "addition_information_content": "null",
                "relatedlinks-TOTAL_FORMS": "0",
                "relatedlinks-INITIAL_FORMS": "0",
                "relatedlinks-MIN_NUM_FORMS": "0",
                "relatedlinks-MAX_NUM_FORMS": "5",
                "related_area_of_expertise-TOTAL_FORMS": "0",
                "related_area_of_expertise-INITIAL_FORMS": "0",
                "related_area_of_expertise-MIN_NUM_FORMS": "0",
                "related_area_of_expertise-MAX_NUM_FORMS": "1000",
                "related_research_centre_pages-TOTAL_FORMS": "0",
                "related_research_centre_pages-INITIAL_FORMS": "0",
                "related_research_centre_pages-MIN_NUM_FORMS": "0",
                "related_research_centre_pages-MAX_NUM_FORMS": "1000",
                "related_schools-TOTAL_FORMS": "0",
                "related_schools-INITIAL_FORMS": "0",
                "related_schools-MIN_NUM_FORMS": "0",
                "related_schools-MAX_NUM_FORMS": "1000",
                "personal_links-TOTAL_FORMS": "0",
                "personal_links-INITIAL_FORMS": "0",
                "personal_links-MIN_NUM_FORMS": "0",
                "personal_links-MAX_NUM_FORMS": "5",
                "slug": "student-monty-python",
            }
        )

    def get_form(self, instance, data=None):
        return self.form_class(instance=instance, data=data)

    def test_the_valid_form(self):
        form = self.get_form(instance=self.student_page, data=self.get_form_data(),)
        self.assertTrue(form.is_valid())

    def test_first_name_required(self):
        data = self.get_form_data()
        data["first_name"] = ""
        form = self.get_form(instance=self.student_page, data=data,)
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required", str(form.errors.get("first_name")))

    def test_last_name_required(self):
        data = self.get_form_data()
        data["last_name"] = ""
        form = self.get_form(instance=self.student_page, data=data,)
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required", str(form.errors.get("last_name")))

    def test_adding_student(self):
        data = self.get_form_data()
        data["student_user_account"] = self.student.id
        form = self.get_form(instance=self.student_page, data=data,)
        self.assertTrue(form.is_valid())

    def test_adding_student_with_page(self):
        # If a student user account has already been related to a page, we shouldn't be able
        # to add them to another
        page = StudentPageFactory()
        page.student_user_account = self.student
        page.save()

        data = self.get_form_data()
        data["student_user_account"] = self.student.id
        form = self.get_form(instance=self.student_page, data=data,)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "The Student you have selected already has a user account",
            str(form.errors.get("student_user_account")),
        )
