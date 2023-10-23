import factory
import wagtail_factories

from rca.programmes.factories import ProgrammeTypeFactory

from .models import ShortCoursePage


class ShortCoursePageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = ShortCoursePage

    title = factory.Faker("text", max_nb_chars=25)
    programme_type = factory.SubFactory(ProgrammeTypeFactory)
    show_register_link = False
