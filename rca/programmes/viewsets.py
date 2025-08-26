from wagtail_orderable_viewset.viewsets import OrderableModelViewSet

from rca.programmes.models import ProgrammeType


class ProgrammeTypeViewSet(OrderableModelViewSet):
    model = ProgrammeType
    form_fields = [
        "display_name",
        "description",
    ]
    list_display = [
        "display_name",
        "sort_order",  # for reference with testing, not required
    ]
    menu_label = "Programme Type"
    icon = "tag"


programme_viewset = ProgrammeTypeViewSet("programme_type")
