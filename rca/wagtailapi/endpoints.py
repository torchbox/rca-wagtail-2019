from wagtail.api.v2 import endpoints
from wagtail.api.v2.filters import (
    FieldsFilter,
    RestrictedChildOfFilter,
    RestrictedDescendantOfFilter,
)
from wagtail.api.v2.serializers import PageSerializer

from rca.wagtailapi import filters


class PagesAPIEndpoint(endpoints.PagesAPIEndpoint):
    base_serializer_class = PageSerializer
    filter_backends = [
        # NOTE that the following filters should be listed before the SearchFilter.
        filters.DegreeLevelFilter,
        filters.SubjectsFilter,
        FieldsFilter,
        RestrictedChildOfFilter,
        RestrictedDescendantOfFilter,
        filters.RelatedSchoolsFilter,
        filters.SearchFilter,
    ]
