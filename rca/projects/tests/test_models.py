from django.test import TestCase
from wagtail.images.tests.utils import get_test_image_file

from rca.home.models import HomePage
from rca.images.models import CustomImage
from rca.projects.models import (
    ProjectPage,
    ProjectPageRelatedResearchPage,
    ProjectPageRelatedSchoolPage,
    ProjectPageResearchTypePlacement,
    ProjectPickerPage,
)
from rca.research.factories import ResearchCentrePageFactory
from rca.schools.factories import SchoolPageFactory
from rca.utils.models import ResearchType
from rca.utils.tests.utils import QueryCountMixin


class ProjectPickerPageTests(QueryCountMixin, TestCase):
    def setUp(self):
        home_page = HomePage.objects.first()
        self.picker = home_page.add_child(
            instance=ProjectPickerPage(title="Projects", slug="projects")
        )
        self.image = image = CustomImage.objects.create(
            title="Image", file=get_test_image_file()
        )
        self.school = SchoolPageFactory(
            parent=home_page, title="School of Design", introduction_image=image
        )
        self.centre = ResearchCentrePageFactory(
            parent=home_page, title="Helen Hamlyn Centre", introduction_image=image
        )
        self.startup = ResearchType.objects.create(title="Start-up")
        self.other_type = ResearchType.objects.create(title="Knowledge exchange")
        self.count = 0

    def add_project(self, school=None, centre=None, research_type=None):
        self.count += 1
        project = ProjectPage(
            title=f"Project {self.count}",
            slug=f"project-{self.count}",
            hero_image=self.image,
        )
        if school:
            project.related_school_pages = [ProjectPageRelatedSchoolPage(page=school)]
        if centre:
            project.related_research_pages = [
                ProjectPageRelatedResearchPage(page=centre)
            ]
        if research_type:
            project.research_types = [
                ProjectPageResearchTypePlacement(research_type=research_type)
            ]
        return self.picker.add_child(instance=project)

    def get_results(self):
        response = self.client.get(self.picker.url)
        return {
            item.title: (item.school, item.is_startup_project)
            for item in response.context["results"]
        }

    def test_cards_show_school_then_centre_then_start_up(self):
        both = self.add_project(school=self.school, centre=self.centre)
        centre_only = self.add_project(centre=self.centre)
        startup = self.add_project(research_type=self.startup)
        startup_with_school = self.add_project(
            school=self.school, research_type=self.startup
        )
        other_type = self.add_project(research_type=self.other_type)
        neither = self.add_project()

        results = self.get_results()

        self.assertEqual(results[both.title][0].pk, self.school.pk)
        self.assertEqual(results[centre_only.title][0].pk, self.centre.pk)
        self.assertEqual(results[startup.title], (None, True))
        self.assertEqual(results[neither.title], (None, False))
        self.assertIs(results[other_type.title][1], False)
        # The card shows "Start-up" instead of the school for this one.
        self.assertIs(results[startup_with_school.title][1], True)

    def test_start_up_projects_are_recognised_without_the_listing_prefetch(self):
        startup = self.add_project(research_type=self.startup)
        other_type = self.add_project(research_type=self.other_type)

        self.assertTrue(ProjectPage.objects.get(pk=startup.pk).is_startup_project)
        self.assertFalse(ProjectPage.objects.get(pk=other_type.pk).is_startup_project)

    def test_query_count_does_not_grow_with_projects(self):
        def add_projects():
            self.add_project(school=self.school, centre=self.centre)
            self.add_project(centre=self.centre)
            self.add_project(research_type=self.startup)

        add_projects()
        self.assertQueryCountDoesNotGrow(
            action=lambda: self.client.get(self.picker.url), grow=add_projects
        )
