from django.db import IntegrityError, connection, transaction
from django.test import TestCase

from rca.home.models import HomePage
from rca.programmes.factories import DegreeLevelFactory, ProgrammePageFactory
from rca.programmes.models import (
    ProgrammeLocation,
    ProgrammeLocationProgrammePage,
    ProgrammePage,
    ProgrammePageDegreeLevel,
    ProgrammeStudyMode,
    ProgrammeStudyModeProgrammePage,
)


class ProgrammePageSwapChildValuesTest(TestCase):
    """
    Editors can swap values between existing inline rows and publish, but
    genuine duplicates are still rejected.
    """

    def setUp(self):
        self.page = ProgrammePageFactory(
            parent=HomePage.objects.first(),
            degree_level=DegreeLevelFactory(),
        )

    def assert_swap_publishes(self, relation, model, page_field, value_field, a, b):
        model.objects.create(**{page_field: self.page, value_field: a})
        model.objects.create(**{page_field: self.page, value_field: b})
        page = ProgrammePage.objects.get(pk=self.page.pk)

        rows = list(getattr(page, relation).order_by("pk"))
        setattr(rows[0], value_field, b)
        setattr(rows[1], value_field, a)
        setattr(page, relation, rows)

        page.save_revision().publish()

        # TestCase never commits, so force deferred constraints to be checked now
        with connection.cursor() as cursor:
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")

        self.assertEqual(
            dict(
                model.objects.filter(**{page_field: page}).values_list(
                    "pk", value_field
                )
            ),
            {rows[0].pk: b.pk, rows[1].pk: a.pk},
        )

    def test_swap_study_modes(self):
        self.assert_swap_publishes(
            "programme_study_modes",
            ProgrammeStudyModeProgrammePage,
            "page",
            "programme_study_mode",
            ProgrammeStudyMode.objects.get(title="Part-time study"),
            ProgrammeStudyMode.objects.get(title="Full-time study"),
        )

    def test_swap_degree_levels(self):
        self.assert_swap_publishes(
            "degree_levels",
            ProgrammePageDegreeLevel,
            "source_page",
            "level",
            DegreeLevelFactory(),
            DegreeLevelFactory(),
        )

    def test_swap_locations(self):
        self.assert_swap_publishes(
            "programme_locations",
            ProgrammeLocationProgrammePage,
            "page",
            "programme_location",
            ProgrammeLocation.objects.create(title="London"),
            ProgrammeLocation.objects.create(title="Online"),
        )

    def test_duplicate_values_are_rejected(self):
        cases = [
            (
                ProgrammeStudyModeProgrammePage,
                "page",
                "programme_study_mode",
                ProgrammeStudyMode.objects.get(title="Full-time study"),
            ),
            (
                ProgrammePageDegreeLevel,
                "source_page",
                "level",
                DegreeLevelFactory(),
            ),
            (
                ProgrammeLocationProgrammePage,
                "page",
                "programme_location",
                ProgrammeLocation.objects.create(title="London"),
            ),
        ]
        for model, page_field, value_field, value in cases:
            with self.subTest(model=model.__name__), transaction.atomic():
                model.objects.create(**{page_field: self.page, value_field: value})
                model.objects.create(**{page_field: self.page, value_field: value})
                with self.assertRaises(IntegrityError):
                    with connection.cursor() as cursor:
                        cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
                # The caught IntegrityError leaves the transaction aborted, so roll
                # back this case's savepoint before the next one
                transaction.set_rollback(True)
