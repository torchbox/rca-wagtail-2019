import factory
import wagtail_factories

from .models import EditorialPage, EditorialType


class EditorialTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EditorialType

    title = factory.Faker("text", max_nb_chars=25)


class EditorialPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = EditorialPage

    title = factory.Faker("text", max_nb_chars=25)
    published_at = factory.Faker("date")
    introduction = factory.Faker("text", max_nb_chars=150)