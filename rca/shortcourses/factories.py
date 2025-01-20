import factory
import wagtail_factories

from rca.programmes.factories import ProgrammeTypeFactory

from .models import ShortCoursePage, ShortCourseProgrammeType


class ShortCoursePageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = ShortCoursePage

    title = factory.Faker("text", max_nb_chars=25)
    show_register_link = False


class ShortCourseProgrammeTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ShortCourseProgrammeType

    page = factory.SubFactory(ShortCoursePageFactory)
    programme_type = factory.SubFactory(ProgrammeTypeFactory)
