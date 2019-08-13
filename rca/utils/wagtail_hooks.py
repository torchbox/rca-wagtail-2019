from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)

from rca.programmes.models import DegreeLevel, ProgrammeType


class DegreeLevelModelAdmin(ModelAdmin):
    model = DegreeLevel
    menu_icon = "tag"


class ProgrammeTypeModelAdmin(ModelAdmin):
    model = ProgrammeType
    menu_icon = "tag"


class TaxonomiesModelAdminGroup(ModelAdminGroup):
    menu_label = "Taxonomies"
    items = (DegreeLevelModelAdmin, ProgrammeTypeModelAdmin)
    menu_icon = "tag"


modeladmin_register(TaxonomiesModelAdminGroup)
