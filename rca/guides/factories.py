import factory
import wagtail_factories

from .models import GuidePage


class GuidePageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = GuidePage

    title = factory.Faker("text", max_nb_chars=25)
