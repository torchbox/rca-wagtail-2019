from django.db.models.signals import post_init
from django.test import TestCase

from rca.editorial.factories import EditorialListingPageFactory, EditorialPageFactory
from rca.editorial.models import EditorialPageRelatedProgramme
from rca.events.factories import EventDetailPageFactory, EventSeriesFactory
from rca.events.models import EventIndexPage
from rca.home.models import HomePage
from rca.people.factories import (
    DirectorateFactory,
    StaffPageFactory,
    StudentIndexPageFactory,
    StudentPageFactory,
)
from rca.people.models import DegreeStatus, StaffIndexPage, StaffPageDirectorate
from rca.programmes.factories import ProgrammePageFactory
from rca.programmes.models import ProgrammePage
from rca.projects.models import (
    ProjectPage,
    ProjectPageResearchTypePlacement,
    ProjectPickerPage,
)
from rca.scholarships.factories import (
    ScholarshipFactory,
    ScholarshipsListingPageFactory,
)
from rca.utils.filter import TabStyleFilter
from rca.utils.models import ResearchType


class TabStyleFilterTests(TestCase):
    def test_has_options_when_its_queryset_has_rows(self):
        ProgrammePageFactory(parent=HomePage.objects.first())

        self.assertTrue(
            TabStyleFilter("Programme", ProgrammePage.objects.all()).has_options
        )
        self.assertFalse(
            TabStyleFilter("Programme", ProgrammePage.objects.none()).has_options
        )


class ListingFilterTabTests(TestCase):
    def setUp(self):
        home_page = HomePage.objects.first()
        self.listing = EditorialListingPageFactory(parent=home_page)
        self.programme = ProgrammePageFactory(parent=home_page)

    def get_listing(self):
        loaded = []

        def record(sender, instance, **kwargs):
            loaded.append(instance)

        post_init.connect(record, sender=ProgrammePage)
        try:
            response = self.client.get(self.listing.url)
        finally:
            post_init.disconnect(record, sender=ProgrammePage)
        return response, loaded

    def test_programme_tab_shows_without_loading_programme_pages(self):
        EditorialPageFactory(
            parent=self.listing,
            related_programmes=[EditorialPageRelatedProgramme(page=self.programme)],
        )

        response, loaded = self.get_listing()

        self.assertContains(response, 'id="tab-programme"')
        self.assertEqual(loaded, [])

    def test_programme_tab_is_hidden_without_related_programmes(self):
        EditorialPageFactory(parent=self.listing)

        response, _ = self.get_listing()

        self.assertNotContains(response, 'id="tab-programme"')


class ListingTabVisibilityTests(TestCase):
    """
    Each listing shows a filter's tab only when the filter has options. These
    cover the listings other than news, which ListingFilterTabTests covers.
    """

    def setUp(self):
        self.home_page = HomePage.objects.first()

    def assertTabs(self, page, shown=(), hidden=()):
        response = self.client.get(page.url)
        for slug in shown:
            self.assertContains(response, f'id="tab-{slug}"')
        for slug in hidden:
            self.assertNotContains(response, f'id="tab-{slug}"')

    def test_events_listing(self):
        listing = self.home_page.add_child(
            instance=EventIndexPage(title="Events", slug="events")
        )
        # The Upcoming/Past tab always shows, even with no events.
        self.assertTabs(listing, shown=["upcomingpast"], hidden=["series"])

        EventDetailPageFactory(parent=listing, series=EventSeriesFactory())
        self.assertTabs(listing, shown=["upcomingpast", "series"])

    def test_staff_listing(self):
        listing = self.home_page.add_child(
            instance=StaffIndexPage(
                title="Staff", slug="staff", introduction="<p>Staff</p>"
            )
        )
        StaffPageFactory(parent=listing)
        self.assertTabs(listing, hidden=["school-centre-or-area", "programme"])

        StaffPageFactory(
            parent=listing,
            related_directorates=[
                StaffPageDirectorate(directorate=DirectorateFactory())
            ],
        )
        self.assertTabs(listing, shown=["school-centre-or-area"], hidden=["programme"])

    def test_student_listing(self):
        listing = StudentIndexPageFactory(parent=self.home_page)
        StudentPageFactory(parent=listing)
        self.assertTabs(listing, hidden=["degree-status", "expertise"])

        StudentPageFactory(
            parent=listing,
            degree_status=DegreeStatus.objects.create(title="Current"),
        )
        self.assertTabs(listing, shown=["degree-status"], hidden=["expertise"])

    def test_projects_listing(self):
        listing = self.home_page.add_child(
            instance=ProjectPickerPage(title="Projects", slug="projects")
        )
        listing.add_child(instance=ProjectPage(title="Plain", slug="plain"))
        self.assertTabs(listing, hidden=["project-type", "sector"])

        listing.add_child(
            instance=ProjectPage(
                title="Start-up",
                slug="start-up",
                research_types=[
                    ProjectPageResearchTypePlacement(
                        research_type=ResearchType.objects.create(title="Start-up")
                    )
                ],
            )
        )
        self.assertTabs(listing, shown=["project-type"], hidden=["sector"])

    def test_scholarships_listing(self):
        listing = ScholarshipsListingPageFactory(parent=self.home_page)
        self.assertTabs(listing, hidden=["programme", "fee-status"])

        ScholarshipFactory(
            eligable_programmes=[ProgrammePageFactory(parent=self.home_page)]
        )
        self.assertTabs(listing, shown=["programme"], hidden=["fee-status"])
