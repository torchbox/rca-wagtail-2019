import factory
import wagtail_factories
from faker import Factory as FakerFactory

from rca.scholarships.models import ScholarshipsListingPage

faker = FakerFactory.create()


class ScholarshipsListingPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = ScholarshipsListingPage

    title = factory.Faker("text", max_nb_chars=25)
    introduction = factory.Faker("text", max_nb_chars=500)
