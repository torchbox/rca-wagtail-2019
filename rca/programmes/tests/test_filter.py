from django.http import QueryDict
from django.test import TestCase

from rca.home.models import HomePage
from rca.programmes.factories import DegreeLevelFactory, ProgrammePageFactory
from rca.programmes.filter import ProgrammeStyleFilter
from rca.programmes.models import ProgrammePage, ProgrammePageDegreeLevel
from rca.utils.tests.utils import QueryCountMixin


class ProgrammeStyleFilterTests(QueryCountMixin, TestCase):
    def setUp(self):
        self.home_page = HomePage.objects.first()
        ma = DegreeLevelFactory(title="MA")
        mfa = DegreeLevelFactory(title="MFA")
        # Created out of slug order, so the options' order by slug is tested.
        sculpture = ProgrammePageFactory(
            parent=self.home_page,
            title="Sculpture",
            slug="sculpture",
            degree_level=None,
        )
        painting = ProgrammePageFactory(
            parent=self.home_page, title="Painting", slug="painting", degree_level=ma
        )
        ProgrammePageDegreeLevel.objects.create(
            source_page=sculpture, level=mfa, sort_order=1
        )
        ProgrammePageDegreeLevel.objects.create(
            source_page=sculpture, level=ma, sort_order=0
        )
        self.ids = [painting.pk, sculpture.pk]

    def get_options(self, selected=""):
        programme_filter = ProgrammeStyleFilter(
            "Programme",
            queryset=ProgrammePage.objects.filter(pk__in=self.ids),
            filter_by="related_programmes__page__slug__in",
            option_value_field="slug",
        )
        programme_filter.apply(ProgrammePage.objects.none(), QueryDict(selected))
        return list(programme_filter)

    def test_options_are_labelled_with_full_titles(self):
        self.assertEqual(
            self.get_options(selected="programme=sculpture"),
            [
                {"id": "painting", "title": "Painting MA", "active": False},
                {"id": "sculpture", "title": "Sculpture MA/MFA", "active": True},
            ],
        )

    def test_query_count_does_not_grow_with_programmes(self):
        def add_programmes():
            self.ids += [
                page.pk
                for page in ProgrammePageFactory.create_batch(5, parent=self.home_page)
            ]

        self.assertQueryCountDoesNotGrow(action=self.get_options, grow=add_programmes)
