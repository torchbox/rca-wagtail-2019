import factory
import wagtail_factories
from faker import Factory as FakerFactory

from .models import (
    DegreeLevel,
    ProgrammePage,
    ProgrammePageProgrammeType,
    ProgrammeType,
)

faker = FakerFactory.create()


class DegreeLevelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DegreeLevel

    title = factory.Faker("text", max_nb_chars=25)


class ProgrammeTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProgrammeType

    display_name = factory.Faker("text", max_nb_chars=25)
    description = factory.Faker("text", max_nb_chars=250)


class ProgrammePageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = ProgrammePage

    title = factory.Faker("text", max_nb_chars=25)
    scholarships_title = factory.Faker("text", max_nb_chars=25)
    scholarships_information = factory.Faker("text", max_nb_chars=100)
    search_description = factory.Faker("text", max_nb_chars=25)
    degree_level = factory.SubFactory(DegreeLevelFactory)


class ProgrammePageProgrammeTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProgrammePageProgrammeType

    page = factory.SubFactory(ProgrammePageFactory)
