import factory
import wagtail_factories
from faker import Factory as FakerFactory

from .models import (
    EELandingPage,
    EnterpriseLandingPage,
    InnovationLandingPage,
    LandingPage,
    ResearchLandingPage,
)

faker = FakerFactory.create()


class EELandingPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = EELandingPage

    title = factory.Faker("text", max_nb_chars=25)


class EnterpriseLandingPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = EnterpriseLandingPage

    title = factory.Faker("text", max_nb_chars=25)


class ResearchLandingPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = ResearchLandingPage

    title = factory.Faker("text", max_nb_chars=25)


class InnovationLandingPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = InnovationLandingPage

    title = factory.Faker("text", max_nb_chars=25)


class LandingPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = LandingPage

    title = factory.Faker("text", max_nb_chars=25)