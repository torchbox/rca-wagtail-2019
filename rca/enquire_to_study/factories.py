import factory
from faker import Factory as FakerFactory

from .models import EnquiryFormSubmission, EnquiryReason, StartDate

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


class EnquiryFormSubmissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EnquiryFormSubmission

    first_name = factory.Sequence(lambda n: f"test-firstname-{n}")
    last_name = factory.Sequence(lambda n: f"test-lastname-{n}")
    email = factory.Sequence(lambda n: f"test-email-{n}@example.org")
    phone_number = faker.phone_number()
    country_of_residence = faker.country_code()
    country_of_citizenship = faker.country_code()
    city = faker.city()
    is_read_data_protection_policy = True
    is_notification_opt_in = True
    enquiry_questions = factory.Sequence(lambda n: f"an example question-{n}")
