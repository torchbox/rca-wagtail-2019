from wagtail.api.v2 import views
from wagtail.api.v2.filters import ChildOfFilter, DescendantOfFilter, FieldsFilter
from wagtail.images.api.v2.views import ImagesAPIViewSet

from rca.navigation.models import NavigationSettings
from rca.utils.models import SitewideAlertSetting
from rca.wagtailapi import filters

from .serializers import RCAImageSerializer, RCAPageSerializer


class PagesAPIViewSet(views.PagesAPIViewSet):
    base_serializer_class = RCAPageSerializer

    filter_backends = [
        # NOTE that the following filters should be listed before the SearchFilter.
        filters.DegreeLevelFilter,
        FieldsFilter,
        ChildOfFilter,
        DescendantOfFilter,
        filters.RelatedSchoolsFilter,
        filters.SubjectsFilter,
        filters.ProgrammeTypesFilter,
        filters.StudyModeFilter,
        filters.DistinctFilter,
        filters.SearchFilter,
    ]

    known_query_parameters = views.PagesAPIViewSet.known_query_parameters.union(
        [
            "full-time",
            "part-time",
        ]
    )

    meta_fields = views.PagesAPIViewSet.meta_fields + [
        "children",
        "descendants",
        "parent",
        "ancestors",
    ]

    listing_default_fields = views.PagesAPIViewSet.listing_default_fields + [
        "children",
    ]

    # Allow the parent field to appear on listings
    detail_only_fields = []


class NavigationAPIViewSet(views.BaseAPIViewSet):
    model = NavigationSettings


class SitewideAlertAPIViewSet(views.BaseAPIViewSet):
    model = SitewideAlertSetting


class RCAImagesViewset(ImagesAPIViewSet):
    base_serializer_class = RCAImageSerializer

    body_fields = ImagesAPIViewSet.body_fields + [
        "thumbnail",
        "original",
        "rca2019_feed_image",
        "rca2019_feed_image_small",
    ]
