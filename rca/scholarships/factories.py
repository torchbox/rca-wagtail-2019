import random

import factory
import wagtail_factories
from faker import Factory as FakerFactory

from rca.home.models import HomePage
from rca.programmes.factories import ProgrammePageFactory
from rca.scholarships.models import (
    Scholarship,
    ScholarshipEnquiryFormSubmission,
    ScholarshipEnquiryFormSubmissionScholarshipOrderable,
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
            parent = HomePage.objects.first()
            extracted = ProgrammePageFactory.generate_batch(
                parent=parent,
                strategy=factory.CREATE_STRATEGY,
                size=random.randint(1, 4),
            )
        obj.eligable_programmes.add(*extracted)

    @factory.post_generation
    def other_criteria(obj, create, extracted, **kwargs):
        if not create:
            return

        if not extracted:
            extracted = ScholarshipFundingFactory.generate_batch(
                strategy=factory.CREATE_STRATEGY,
                size=random.randint(1, 4),
            )
        obj.other_criteria.add(*extracted)

    @factory.post_generation
    def fee_statuses(obj, create, extracted, **kwargs):
        if not create:
            return

        if not extracted:
            extracted = ScholarshipFeeStatusFactory.generate_batch(
                strategy=factory.CREATE_STRATEGY,
                size=random.randint(1, 4),
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
    scholarship_listing_title = factory.Faker("text", max_nb_chars=25)
    scholarship_listing_sub_title = factory.Faker("text", max_nb_chars=50)
    # TODO: add field for scholarship_application_steps


class ScholarshipEnquiryFormSubmissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ScholarshipEnquiryFormSubmission

    first_name = factory.Sequence(lambda n: "test-firstname-%d" % n)
    last_name = factory.Sequence(lambda n: "test-lastname-%d" % n)
    email = factory.Sequence(lambda n: "test-email-%d@example.org" % n)
    rca_id_number = faker.random_number()
    is_read_data_protection_policy = True
    is_notification_opt_in = True
    programme = factory.SubFactory(ProgrammePageFactory)

    @factory.post_generation
    def scholarships(obj, create, extracted, **kwargs):
        if not create:
            return

        if not extracted:
            extracted = ScholarshipFactory.generate_batch(
                strategy=factory.CREATE_STRATEGY,
                size=2,
            )
        for scholarship in extracted:
            ScholarshipEnquiryFormSubmissionScholarshipOrderable.objects.create(
                scholarship_submission=obj,
                scholarship=scholarship,
            )
