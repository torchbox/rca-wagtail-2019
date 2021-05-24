from django.test import TestCase
from wagtail.tests.utils.form_data import nested_form_data
from wagtail_factories import CollectionFactory

from rca.people.factories import StudentPageFactory


class TestStudentPageForm(TestCase):
    def setUp(self):
        self.student_page = StudentPageFactory()
        self.form_class = self.student_page.get_edit_handler().get_form_class()
        self.collection = CollectionFactory(name="Student: foxmulder")

    def get_form_data(self):
        return nested_form_data(
            {
                "title": "Fox Mulder",
                "slug": "fox",
                "student_title": "Dr",
                "first_name": "Fox",
                "last_name": "Mulder",
                "profile_image": "",
                "email": "",
                "programme": "",
                "degree_start_date": "",
                "degree_end_date": "",
                "degree_status": "",
                "link_to_final_thesis": "",
                "related_supervisor-TOTAL_FORMS": "0",
                "related_supervisor-INITIAL_FORMS": "0",
                "related_supervisor-MIN_NUM_FORMS": "0",
                "related_supervisor-MAX_NUM_FORMS": "1000",
                "introduction": "",
                "bio": "",
                "related_project_pages-TOTAL_FORMS": "0",
                "related_project_pages-INITIAL_FORMS": "0",
                "related_project_pages-MIN_NUM_FORMS": "0",
                "related_project_pages-MAX_NUM_FORMS": "5",
                "gallery_slides-TOTAL_FORMS": "0",
                "gallery_slides-INITIAL_FORMS": "0",
                "gallery_slides-MIN_NUM_FORMS": "0",
                "gallery_slides-MAX_NUM_FORMS": "5",
                "biography": "",
                "degrees": "",
                "experience": "",
                "awards": "",
                "funding": "",
                "exhibitions": "",
                "publications": "",
                "research_outputs": "",
                "conferences": "",
                "additional_information_title": "",
                "addition_information_content": "",
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
                "student_funding": "null",
                "seo_title": "",
                "show_in_menus": "on",
                "search_description": "",
                "social_image": "",
                "social_text": "",
                "listing_image": "",
                "listing_title": "",
                "listing_summary": "",
                "go_live_at": "",
                "expire_at": "",
                "student_user_image_collection": self.collection.id,
                "student_user_account": "",
            }
        )

    def get_form(self, instance, data=None):
        return self.form_class(instance=instance, data=data)

    def test_form_not_valid(self):
        print(self.get_form_data())
        form = self.get_form(instance=self.student_page, data=self.get_form_data())
        self.assertFalse(form.is_valid())
