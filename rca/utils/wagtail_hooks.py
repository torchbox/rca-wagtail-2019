from django.utils.html import escape
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    ModelAdminGroup,
    modeladmin_register,
)
from wagtail.core import hooks
from wagtail.core.rich_text import LinkHandler
from wagtailorderable.modeladmin.mixins import OrderableMixin

from rca.people.models import AreaOfExpertise, Directorate
from rca.programmes.models import DegreeLevel, ProgrammeType, Subject
from rca.utils.models import ResearchTheme, ResearchType, Sector
from rca.utils.templatetags.util_tags import is_external


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


class DirectorateModelAdmin(ModelAdmin):
    model = Directorate
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
    )
    menu_icon = "tag"


modeladmin_register(TaxonomiesModelAdminGroup)


class TargetBlankExternalLinkHandler(LinkHandler):
    identifier = "external"

    @classmethod
    def expand_db_attributes(cls, attrs):
        href = attrs["href"]
        target = "target=\"_blank\"" if is_external(href) else ""
        return f'<a href="{escape(href)}"{target}>'


@hooks.register("register_rich_text_features")
def register_external_link(features):
    features.register_link_type(TargetBlankExternalLinkHandler)
