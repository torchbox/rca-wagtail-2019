from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from wagtailorderable.modeladmin.mixins import OrderableMixin

from rca.people.models import AreaOfExpertise
from rca.programmes.models import DegreeLevel, ProgrammeType, Subject
from rca.utils.models import ResearchType


class DegreeLevelModelAdmin(ModelAdmin):
    model = DegreeLevel
    menu_icon = "tag"


class SubjectModelAdmin(ModelAdmin):
    model = Subject
    menu_icon = "tag"


class ProgrammeTypeModelAdmin(OrderableMixin, ModelAdmin):
    model = ProgrammeType
    menu_icon = "tag"
    ordering = ["sort_order"]


class ResearchTypeModelAdmin(ModelAdmin):
    model = ResearchType
    menu_icon = "tag"


class AreaOfExpertiseModelAdmin(ModelAdmin):
    model = AreaOfExpertise
    menu_icon = "tag"


class TaxonomiesModelAdminGroup(ModelAdminGroup):
    menu_label = "Taxonomies"
    items = (
        DegreeLevelModelAdmin,
        ProgrammeTypeModelAdmin,
        SubjectModelAdmin,
        ResearchTypeModelAdmin,
        AreaOfExpertiseModelAdmin,
    )
    menu_icon = "tag"


modeladmin_register(TaxonomiesModelAdminGroup)
