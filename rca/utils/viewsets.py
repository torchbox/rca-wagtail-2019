from wagtail.admin.views.generic.models import IndexView
from wagtail.admin.viewsets.model import ModelViewSet, ModelViewSetGroup

from rca.editorial.models import Author, EditorialType
from rca.events.models import (
    EventAvailability,
    EventEligibility,
    EventLocation,
    EventSeries,
    EventType,
)
from rca.people.models import AreaOfExpertise, DegreeStatus, DegreeType, Directorate
from rca.programmes.models import (
    DegreeLevel,
    ProgrammeLocation,
    ProgrammeStudyMode,
    ProgrammeType,
    Subject,
)
from rca.scholarships.models import (
    ScholarshipFeeStatus,
    ScholarshipFunding,
    ScholarshipLocation,
)
from rca.utils.models import ResearchTheme, ResearchType, Sector


class TaxonomyViewSet(ModelViewSet):
    """Base viewset for the taxonomy models. Builds the create/edit form from
    all editable model fields (matching the previous modeladmin behaviour) and
    uses the shared ``tag`` icon."""

    icon = "tag"
    exclude_form_fields = []


class DegreeLevelViewSet(TaxonomyViewSet):
    model = DegreeLevel


class AuthorViewSet(TaxonomyViewSet):
    model = Author


class SubjectViewSet(TaxonomyViewSet):
    model = Subject


class ProgrammeStudyModeIndexView(IndexView):
    """
    Hide the "Add" button if there are >= 2 instances.
    """

    @property
    def header_buttons(self):
        buttons = super().header_buttons
        if ProgrammeStudyMode.objects.count() >= 2:
            buttons = [button for button in buttons if button is not self.add_button]
        return buttons


class ProgrammeStudyModeViewSet(TaxonomyViewSet):
    model = ProgrammeStudyMode
    index_view_class = ProgrammeStudyModeIndexView


class ProgrammeTypeViewSet(TaxonomyViewSet):
    # ``ProgrammeType`` subclasses ``wagtail.models.Orderable``, so the viewset
    # auto-detects ``sort_order_field`` and offers native drag-and-drop reorder.
    model = ProgrammeType
    ordering = ["sort_order"]


class ProgrammeLocationViewSet(TaxonomyViewSet):
    model = ProgrammeLocation


class ResearchTypeViewSet(TaxonomyViewSet):
    model = ResearchType


class AreaOfExpertiseViewSet(TaxonomyViewSet):
    model = AreaOfExpertise


class ResearchThemeViewSet(TaxonomyViewSet):
    model = ResearchTheme


class SectorViewSet(TaxonomyViewSet):
    model = Sector


class DegreeTypeViewSet(TaxonomyViewSet):
    model = DegreeType


class DegreeStatusViewSet(TaxonomyViewSet):
    model = DegreeStatus


class DirectorateViewSet(TaxonomyViewSet):
    model = Directorate


class EventAvailabilityViewSet(TaxonomyViewSet):
    model = EventAvailability
    menu_label = "Event Availability"


class EventEligibilityViewSet(TaxonomyViewSet):
    model = EventEligibility
    menu_label = "Event Eligibility"


class EventLocationViewSet(TaxonomyViewSet):
    model = EventLocation
    menu_label = "Event Locations"


class EventSeriesViewSet(TaxonomyViewSet):
    model = EventSeries
    menu_label = "Event Series"


class EventTypeViewSet(TaxonomyViewSet):
    model = EventType


class EditorialTypeViewSet(TaxonomyViewSet):
    model = EditorialType


class ScholarshipFeeStatusViewSet(TaxonomyViewSet):
    model = ScholarshipFeeStatus


class ScholarshipFundingViewSet(TaxonomyViewSet):
    model = ScholarshipFunding


class ScholarshipLocationViewSet(TaxonomyViewSet):
    model = ScholarshipLocation


class TaxonomiesViewSetGroup(ModelViewSetGroup):
    menu_label = "Taxonomies"
    menu_icon = "tag"
    items = (
        DegreeLevelViewSet,
        ProgrammeTypeViewSet,
        ProgrammeStudyModeViewSet,
        ProgrammeLocationViewSet,
        SubjectViewSet,
        ResearchTypeViewSet,
        AreaOfExpertiseViewSet,
        SectorViewSet,
        ResearchThemeViewSet,
        DirectorateViewSet,
        DegreeTypeViewSet,
        DegreeStatusViewSet,
        EventAvailabilityViewSet,
        EventEligibilityViewSet,
        EventLocationViewSet,
        EventSeriesViewSet,
        EventTypeViewSet,
        AuthorViewSet,
        EditorialTypeViewSet,
        ScholarshipFeeStatusViewSet,
        ScholarshipFundingViewSet,
        ScholarshipLocationViewSet,
    )
