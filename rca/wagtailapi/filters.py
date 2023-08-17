from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from rest_framework import filters
from wagtail.api.v2.utils import BadRequestError
from wagtail.models import Page
from wagtail.search.backends import get_search_backend
from wagtail.search.backends.base import FilterFieldError, OrderByFieldError

from rca.programmes.models import ProgrammeStudyMode
from rca.shortcourses.models import ShortCoursePage


class DegreeLevelFilter(filters.BaseFilterBackend):
    """
    Allows to filter pages by one or multiple projects
    """

    def filter_queryset(self, request, queryset, view):
        pks = request.GET.getlist("project", [])

        if pks:
            queryset = queryset.filter(degree_level__in=pks)

        return queryset.order_by("title").live()


class SubjectsFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        try:
            queryset.model._meta.get_field("subjects")
            subject_ids = [int(id) for id in request.GET.getlist("subjects", [])]
            if subject_ids:
                queryset = (
                    queryset.model.objects.filter(subjects__subject_id__in=subject_ids)
                    .order_by("title")
                    .live()
                )
            return queryset
        except FieldDoesNotExist:
            return queryset


class RelatedSchoolsFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        try:
            # Check if the related pages field exists
            queryset.model._meta.get_field("related_schools_and_research_pages")
            related_schools_and_research_page_ids = request.GET.get(
                "related_schools_and_research_pages"
            )

            if related_schools_and_research_page_ids:
                # Get the school/research page we are applying as a filter as a queryset
                filter_page_qs = Page.objects.live().filter(
                    id=related_schools_and_research_page_ids
                )
                # Create a queryset to return which contains pages that have filter_page_qs
                # as a relationship
                queryset = (
                    queryset.model.objects.filter(
                        related_schools_and_research_pages__page_id__in=filter_page_qs.values_list(
                            "pk", flat=True
                        )
                    )
                    .order_by("title")
                    .live()
                )
            return queryset
        except FieldDoesNotExist:
            return queryset


class StudyModeFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        try:
            queryset.model._meta.get_field("programme_study_modes")
            study_mode_ids = request.GET.get("programme_study_modes")

            if study_mode_ids:
                # Get the programme study modes we are applying as a filter as a queryset
                filter_study_mode_qs = ProgrammeStudyMode.objects.filter(
                    id=study_mode_ids
                )
                # Create a queryset to return which contains pages that have filter_study_mode_qs
                # as a relationship
                queryset = (
                    queryset.model.objects.filter(
                        programme_study_modes__programme_study_mode_id__in=filter_study_mode_qs.values_list(
                            "pk", flat=True
                        )
                    )
                    .order_by("title")
                    .live()
                )
            return queryset
        except FieldDoesNotExist:
            try:
                study_modes_attr = getattr(
                    queryset.model, "programme_study_modes", None
                )
                if study_modes_attr:
                    # add all live ShortCoursePages to the current queryset
                    queryset = queryset | ShortCoursePage.objects.live()
            except AttributeError:
                pass

            return queryset


class SearchFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        """
        This overrides the wagtail core api filters.SearchFilter
        so we can provide autocomplet/fuzzy text matching with
        sb.autocomplete
        """
        search_enabled = getattr(settings, "WAGTAILAPI_SEARCH_ENABLED", True)

        if "search" in request.GET:
            if not search_enabled:
                raise BadRequestError("search is disabled")

            # Searching and filtering by tag at the same time is not supported
            if getattr(queryset, "_filtered_by_tag", False):
                raise BadRequestError(
                    "filtering by tag with a search query is not supported"
                )

            search_query = request.GET["search"]
            search_operator = request.GET.get("search_operator", None)
            order_by_relevance = "order" not in request.GET

            sb = get_search_backend()
            try:
                queryset = sb.autocomplete(
                    search_query,
                    queryset,
                    operator=search_operator,
                    order_by_relevance=order_by_relevance,
                )
            except FilterFieldError as e:
                raise BadRequestError(
                    "cannot filter by '{}' while searching (field is not indexed)".format(
                        e.field_name
                    )
                )
            except OrderByFieldError as e:
                raise BadRequestError(
                    "cannot order by '{}' while searching (field is not indexed)".format(
                        e.field_name
                    )
                )

        return queryset
