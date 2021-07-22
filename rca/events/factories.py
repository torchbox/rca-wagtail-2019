import factory
import wagtail_factories

from .models import EventDetailPage, EventSeries, EventType


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
