from django.test import TestCase
from wagtail.images.tests.utils import get_test_image_file

from rca.home.models import HomePage
from rca.images.models import CustomImage
from rca.people.factories import DirectorateFactory
from rca.people.filter import SchoolCentreDirectorateFilter
from rca.people.models import Directorate
from rca.research.factories import ResearchCentrePageFactory
from rca.research.models import ResearchCentrePage
from rca.schools.factories import SchoolPageFactory
from rca.schools.models import SchoolPage


class SchoolCentreDirectorateFilterTests(TestCase):
    def setUp(self):
        home_page = HomePage.objects.first()
        image = CustomImage.objects.create(title="Image", file=get_test_image_file())
        SchoolPageFactory(parent=home_page, introduction_image=image)
        ResearchCentrePageFactory(parent=home_page, introduction_image=image)
        DirectorateFactory()

    def make_filter(self, schools=False, centres=False, directorates=False):
        def queryset(model, has_rows):
            return model.objects.all() if has_rows else model.objects.none()

        return SchoolCentreDirectorateFilter(
            "School, Centre or Area",
            school_queryset=queryset(SchoolPage, schools),
            centre_queryset=queryset(ResearchCentrePage, centres),
            directorate_queryset=queryset(Directorate, directorates),
        )

    def test_has_options_with_only_schools(self):
        self.assertTrue(self.make_filter(schools=True).has_options)

    def test_has_options_with_only_centres(self):
        self.assertTrue(self.make_filter(centres=True).has_options)

    def test_has_options_with_only_directorates(self):
        self.assertTrue(self.make_filter(directorates=True).has_options)

    def test_has_no_options_when_all_are_empty(self):
        self.assertFalse(self.make_filter().has_options)
