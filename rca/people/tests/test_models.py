from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse
from wagtail.models import Collection, GroupCollectionPermission, GroupPagePermission
from wagtail.test.utils import WagtailPageTestCase, WagtailTestUtils
from wagtail.test.utils.form_data import inline_formset, rich_text
from wagtail_factories import CollectionFactory

from rca.home.models import HomePage
from rca.people.factories import (
    DirectorateFactory,
    StaffPageFactory,
    StudentIndexPageFactory,
    StudentPageFactory,
)
from rca.people.models import StudentIndexPage, StudentPage
from rca.users.factories import UserFactory
from rca.users.models import User


class TestStudentPageFactory(TestCase):
    def test_factories(self):
        StudentPageFactory()
        StudentIndexPageFactory()
        DirectorateFactory()
        StaffPageFactory()


class TestStudentIndexPage(WagtailPageTestCase):
    def setUp(self):
        self.home_page = HomePage.objects.first()
        self.user = self.login()

    def test_page_count_rules(self):
        # Only a single Student listing page should be creatable.
        # It's tied to signing up students, see rca.users.signals
        self.assertTrue(StudentIndexPage.can_create_at(self.home_page))
        self.home_page.add_child(
            instance=StudentIndexPage(
                title="Students", slug="students", introduction="Students"
            )
        )
        # A second person listing page should not be creatable
        self.assertFalse(StudentIndexPage.can_create_at(self.home_page))


class TestStudentPage(WagtailPageTestCase):
    def setUp(self):
        super().setUp()
        self.home_page = HomePage.objects.first()
        self.home_page.add_child(
            instance=StudentIndexPage(
                title="Students", slug="students", introduction="Students"
            )
        )
        self.student_index = StudentIndexPage.objects.first()

        self.student = User.objects.create_user(
            username="danascully",
            first_name="dana",
            last_name="Scully",
            email="ds@fbi.com",
            password="1234",
        )
        self.collection = CollectionFactory(name="Student: dana scully")

        student_group = Group.objects.get(name="Students")
        # Add the student group
        self.student.groups.add(student_group)
        self.student.save()

    def test_creating_creates_permision_group(self):
        """Creating a student page WITH a student user account and student image
        collection value should generate a group with permission on page.save()
        """
        self.student_index.add_child(
            instance=StudentPage(
                title="Dana Scully",
                slug="a-student",
                first_name="dana",
                last_name="student",
                student_user_image_collection=self.collection,
                student_user_account=self.student,
            )
        )
        student_page = StudentPage.objects.get(slug="a-student")
        group = Group.objects.get(name=f"Student: {self.student.username}")
        page_permission = GroupPagePermission.objects.filter(
            group=group,
            page=student_page,
            permission=Permission.objects.get(
                content_type__app_label="wagtailcore", codename="change_page"
            ),
        )
        edit_collection_permission = GroupCollectionPermission.objects.get(
            group=group,
            collection=Collection.objects.get(name=self.collection),
            permission=Permission.objects.get(codename="add_image"),
        )
        choose_collection_permission = GroupCollectionPermission.objects.get(
            group=group,
            collection=Collection.objects.get(name=self.collection),
            permission=Permission.objects.get(codename="choose_image"),
        )
        self.assertTrue(group)
        self.assertTrue(page_permission)
        self.assertTrue(edit_collection_permission)
        self.assertTrue(choose_collection_permission)

    def test_creating_does_not_create_permision_group(self):
        """Creating a student page WITHOUT a student user account and student image
        collection value should NOT generate a group with permission on page.save()
        """
        self.student_index.add_child(
            instance=StudentPage(
                title="Dana Scully",
                slug="a-student",
                first_name="dana",
                last_name="student",
            )
        )
        group = Group.objects.filter(name=f"Student: {self.student.username}")
        self.assertFalse(group)


class TestStudentPageCreation(TestCase, WagtailTestUtils):

    create_view_name = "student_account_create"

    def setUp(self):
        super().setUp()
        self.user = UserFactory(is_superuser=True)
        self.client.force_login(self.user)
        self.home_page = HomePage.objects.first()
        self.student_index = StudentIndexPageFactory(
            parent=self.home_page,
            title="Students",
            slug="students",
            introduction="students",
        )
        self.student = User.objects.create_user(
            username="foxmulder",
            first_name="fox",
            last_name="mulder",
            email="fm@fbi.com",
            password="1234",
        )
        self.collection = CollectionFactory(name="Student: fox mulder")

        student_group = Group.objects.get(name="Students")
        # Add the student group
        self.student.groups.add(student_group)
        self.student.save()

        self.post_data = {
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
            "bio": rich_text(""),
            "related_project_pages-TOTAL_FORMS": "0",
            "related_project_pages-INITIAL_FORMS": "0",
            "related_project_pages-MIN_NUM_FORMS": "0",
            "related_project_pages-MAX_NUM_FORMS": "5",
            "gallery_slides-TOTAL_FORMS": "0",
            "gallery_slides-INITIAL_FORMS": "0",
            "gallery_slides-MIN_NUM_FORMS": "0",
            "gallery_slides-MAX_NUM_FORMS": "5",
            "biography": rich_text(""),
            "degrees": rich_text(""),
            "experience": rich_text(""),
            "awards": rich_text(""),
            "funding": rich_text(""),
            "exhibitions": rich_text(""),
            "publications": rich_text(""),
            "research_outputs": rich_text(""),
            "conferences": rich_text(""),
            "additional_information_title": "",
            "addition_information_content": rich_text(""),
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
            "related_project_pages": inline_formset([]),
            "gallery_slides": inline_formset([]),
            "related_supervisor": inline_formset([]),
            "relatedlinks": inline_formset([]),
            "related_area_of_expertise": inline_formset([]),
            "related_research_centre_pages": inline_formset([]),
            "related_schools": inline_formset([]),
            "personal_links": inline_formset([]),
            "student_funding": rich_text(""),
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
            "student_user_image_collection": "",
            "student_user_account": "",
        }

    def test_create_page(self):

        self.client.post(
            reverse(
                "wagtailadmin_pages:add",
                args=("people", "studentpage", self.student_index.id),
            ),
            self.post_data,
        )
        # Check the page exists
        page = StudentPage.objects.get(slug="fox")
        self.assertTrue(page)

    def test_create_page_validation_no_user(self):
        data = self.post_data
        data["student_user_image_collection"] = self.collection.id
        response = self.client.post(
            reverse(
                "wagtailadmin_pages:add",
                args=("people", "studentpage", self.student_index.id),
            ),
            data,
        )
        # Check the error has been added to the page
        self.assertContains(
            response,
            "If you are adding an image collection to use on this profile, "
            "a student user account must be added.",
        )

    def test_create_page_validation_no_collection(self):
        data = self.post_data
        data["student_user_account"] = self.student.id
        response = self.client.post(
            reverse(
                "wagtailadmin_pages:add",
                args=("people", "studentpage", self.student_index.id),
            ),
            data,
        )
        # Check the error has been added to the page
        self.assertContains(
            response,
            "If you are adding a student user account so a student can access "
            "this page, an image collection must be added.",
        )
