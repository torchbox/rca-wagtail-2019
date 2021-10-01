import factory
import wagtail_factories
from faker import Factory as FakerFactory

from .models import DonationFormPage

faker = FakerFactory.create()


class DonationFormPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = DonationFormPage

    title = factory.Faker("text", max_nb_chars=25)
    form_id = "donate1"
