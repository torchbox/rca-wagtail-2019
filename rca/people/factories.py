import factory
import wagtail_factories
from faker import Factory as FakerFactory

from .models import StudentIndexPage, StudentPage

faker = FakerFactory.create()


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
