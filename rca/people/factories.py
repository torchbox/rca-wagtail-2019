import factory
import wagtail_factories
from faker import Factory as FakerFactory

from .models import Directorate, StaffPage, StudentIndexPage, StudentPage

faker = FakerFactory.create()


class DirectorateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Directorate

    title = factory.Faker("text", max_nb_chars=25)


class StudentPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = StudentPage

    title = factory.Faker("text", max_nb_chars=25)
    first_name = factory.Faker("text", max_nb_chars=25)
    last_name = factory.Faker("text", max_nb_chars=25)


class StudentIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = StudentIndexPage

    title = factory.Faker("text", max_nb_chars=25)
    introduction = factory.Faker("text", max_nb_chars=250)


class StaffPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = StaffPage

    title = factory.Faker("text", max_nb_chars=25)
    first_name = factory.Faker("text", max_nb_chars=25)
    last_name = factory.Faker("text", max_nb_chars=25)
