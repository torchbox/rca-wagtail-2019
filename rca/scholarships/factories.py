import random

import factory
import wagtail_factories
from faker import Factory as FakerFactory

from rca.programmes.factories import ProgrammePageFactory
from rca.scholarships.models import (
    Scholarship,
    ScholarshipFeeStatus,
    ScholarshipFunding,
    ScholarshipLocation,
    ScholarshipsListingPage,
)

faker = FakerFactory.create()


class ScholarshipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Scholarship

    title = factory.Faker("text", max_nb_chars=25)
    summary = factory.Faker("text", max_nb_chars=200)
    value = factory.Faker("text", max_nb_chars=50)

    @factory.post_generation
    def eligable_programmes(obj, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if not extracted:
            extracted = ProgrammePageFactory.generate_batch(
                strategy=factory.CREATE_STRATEGY, size=random.randint(1, 4),
            )
        obj.eligable_programmes.add(*extracted)

    @factory.post_generation
    def funding_categories(obj, create, extracted, **kwargs):
        if not create:
            return

        if not extracted:
            extracted = ScholarshipFundingFactory.generate_batch(
                strategy=factory.CREATE_STRATEGY, size=random.randint(1, 4),
            )
        obj.funding_categories.add(*extracted)

    @factory.post_generation
    def fee_statuses(obj, create, extracted, **kwargs):
        if not create:
            return

        if not extracted:
            extracted = ScholarshipFeeStatusFactory.generate_batch(
                strategy=factory.CREATE_STRATEGY, size=random.randint(1, 4),
            )
        obj.fee_statuses.add(*extracted)


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
