import factory
import wagtail_factories

from .models import ResearchCentrePage


class ResearchCentrePageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = ResearchCentrePage

    title = factory.Faker("text", max_nb_chars=25)
    related_programmes_title = factory.Faker("text", max_nb_chars=25)
