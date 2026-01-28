import factory
import wagtail_factories
from django.utils import timezone
from wagtail_personalisation.models import Segment

from rca.personalisation.models import (
    CollapsibleNavigationCallToAction,
    EmbeddedFooterCallToAction,
    EventCountdownCallToAction,
    UserActionCallToAction,
)


# In the tests, we mock what segments are returned so this factory is
# just so we can plug it in the orderables.
class SegmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Segment

    name = factory.Faker("text", max_nb_chars=25)
    type = "static"
    count = 0


class UserActionCallToActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserActionCallToAction

    title = factory.Faker("text", max_nb_chars=40)
    description = factory.Faker("text", max_nb_chars=65)
    image = factory.SubFactory(wagtail_factories.ImageFactory)
    user_action = "page_load"
    link_label = "Click here"
    go_live_at = factory.LazyFunction(timezone.now)


class EmbeddedFooterCallToActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmbeddedFooterCallToAction

    title = factory.Faker("text", max_nb_chars=40)
    description = factory.Faker("text", max_nb_chars=65)
    link_label = "Click here"
    go_live_at = factory.LazyFunction(timezone.now)


class EventCountdownCallToActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventCountdownCallToAction

    title = factory.Faker("text", max_nb_chars=40)
    user_action = "page_load"
    link_label = "Register now"
    go_live_at = factory.LazyFunction(timezone.now)


class CollapsibleNavigationCallToActionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CollapsibleNavigationCallToAction

    title = factory.Faker("text", max_nb_chars=255)
    go_live_at = factory.LazyFunction(timezone.now)
