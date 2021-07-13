from django.utils.html import escape
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from wagtail.core import hooks
from wagtail.core.rich_text import LinkHandler
from wagtailorderable.modeladmin.mixins import OrderableMixin

from rca.events.models import EventType
from rca.people.models import AreaOfExpertise, DegreeStatus, DegreeType, Directorate
from rca.programmes.models import DegreeLevel, ProgrammeType, Subject
from rca.utils.models import ResearchTheme, ResearchType, Sector


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


class ResearchThemeModelAdmin(ModelAdmin):
    model = ResearchTheme
    menu_icon = "tag"


class SectorModelAdmin(ModelAdmin):
    model = Sector
    menu_icon = "tag"


class DegreeTypeModelAdmin(ModelAdmin):
    model = DegreeType
    menu_icon = "tag"


class DegreeStatusModelAdmin(ModelAdmin):
    model = DegreeStatus
    menu_icon = "tag"


class DirectorateModelAdmin(ModelAdmin):
    model = Directorate
    menu_icon = "tag"


class EventTypeModelAdmin(ModelAdmin):
    model = EventType
    menu_icon = "tag"


class TaxonomiesModelAdminGroup(ModelAdminGroup):
    menu_label = "Taxonomies"
    items = (
        DegreeLevelModelAdmin,
        ProgrammeTypeModelAdmin,
        SubjectModelAdmin,
        ResearchTypeModelAdmin,
        AreaOfExpertiseModelAdmin,
        SectorModelAdmin,
        ResearchThemeModelAdmin,
        DirectorateModelAdmin,
        DegreeTypeModelAdmin,
        DegreeStatusModelAdmin,
        EventTypeModelAdmin,
    )
    menu_icon = "tag"


modeladmin_register(TaxonomiesModelAdminGroup)


class TargetBlankExternalLinkHandler(LinkHandler):
    identifier = "external"

    @classmethod
    def expand_db_attributes(cls, attrs):
        href = attrs["href"]
        return f'<a href="{escape(href)}" target="_blank">'


@hooks.register("register_rich_text_features")
def register_external_link(features):
    features.register_link_type(TargetBlankExternalLinkHandler)
