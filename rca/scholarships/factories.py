import factory
import wagtail_factories
from faker import Factory as FakerFactory

from rca.scholarships.models import (
    ScholarshipFeeStatus,
    ScholarshipFunding,
    ScholarshipLocation,
    ScholarshipsListingPage,
)

faker = FakerFactory.create()


class ScholarshipFeeStatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ScholarshipFeeStatus

    title = factory.Faker("text", max_nb_chars=25)


class ScholarshipFundingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ScholarshipFunding

    title = factory.Faker("text", max_nb_chars=25)


class ScholarshipLocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ScholarshipLocation

    title = factory.Faker("text", max_nb_chars=25)


class ScholarshipsListingPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = ScholarshipsListingPage

    title = factory.Faker("text", max_nb_chars=25)
    introduction = factory.Faker("text", max_nb_chars=500)
