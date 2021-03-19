import factory
from faker import Factory as FakerFactory

from .models import EnquiryReason, StartDate

faker = FakerFactory.create()


class StartDateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StartDate

    label = factory.Faker("text", max_nb_chars=25)
    start_date = factory.Faker("date")


class EnquiryReasonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EnquiryReason

    reason = factory.Faker("text", max_nb_chars=25)
