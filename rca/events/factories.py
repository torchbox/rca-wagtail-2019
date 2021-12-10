import factory
import wagtail_factories

from .models import (
    EventAvailability,
    EventDetailPage,
    EventEligibility,
    EventLocation,
    EventSeries,
    EventType,
)


class EventSeriesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventSeries

    title = factory.Faker("text", max_nb_chars=25)
    introduction = factory.Faker("text", max_nb_chars=150)


class EventTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventType

    title = factory.Faker("text", max_nb_chars=25)


class EventDetailPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = EventDetailPage

    title = factory.Faker("text", max_nb_chars=25)
    introduction = factory.Faker("text", max_nb_chars=150)
    start_date = factory.Faker("date")
    end_date = factory.Faker("date")
    event_type = factory.SubFactory(EventTypeFactory)


class EventAvailabilityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventAvailability

    title = factory.Faker("text", max_nb_chars=25)


class EventLocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventLocation

    title = factory.Faker("text", max_nb_chars=25)


class EventEligibilityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventEligibility
