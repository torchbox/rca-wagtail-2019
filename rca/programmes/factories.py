import factory
import wagtail_factories

from .models import DegreeLevel, ProgrammePage, ProgrammeType


class DegreeLevelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DegreeLevel

    title = factory.Faker("text", max_nb_chars=25)


class ProgrammeTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProgrammeType

    display_name = factory.Faker("text", max_nb_chars=128)
    description = factory.Faker("text", max_nb_chars=500)


class ProgrammePageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = ProgrammePage

    title = factory.Faker("text", max_nb_chars=25)
    degree_level = factory.SubFactory(DegreeLevelFactory)
    programme_type = factory.SubFactory(ProgrammeTypeFactory)
    scholarships_title = factory.Faker("text", max_nb_chars=25)
    scholarships_information = factory.Faker("text", max_nb_chars=25)
    search_description = factory.Faker("text", max_nb_chars=25)
