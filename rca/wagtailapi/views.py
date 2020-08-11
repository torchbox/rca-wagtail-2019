from wagtail.api.v2 import views
from wagtail.api.v2.filters import ChildOfFilter, DescendantOfFilter, FieldsFilter
from wagtail.api.v2.serializers import PageSerializer

from rca.navigation.models import NavigationSettings
from rca.utils.models import SitewideAlertSetting
from rca.wagtailapi import filters


class PagesAPIViewSet(views.PagesAPIViewSet):
    base_serializer_class = PageSerializer
    filter_backends = [
        # NOTE that the following filters should be listed before the SearchFilter.
        filters.DegreeLevelFilter,
        FieldsFilter,
        ChildOfFilter,
        DescendantOfFilter,
        filters.RelatedSchoolsFilter,
        filters.SubjectsFilter,
        filters.SearchFilter,
    ]


class NavigationAPIViewSet(views.BaseAPIViewSet):
    model = NavigationSettings


class SitewideAlertAPIViewSet(views.BaseAPIViewSet):
    model = SitewideAlertSetting
