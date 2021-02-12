import factory
import wagtail_factories
from faker import Factory as FakerFactory

from .models import SchoolPage

faker = FakerFactory.create()


class SchoolPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = SchoolPage

    title = factory.Faker("text", max_nb_chars=25)
    introduction = factory.Faker("text", max_nb_chars=250)
    body = factory.Faker("text", max_nb_chars=250)
