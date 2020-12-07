from django.db.models import Q
from django.utils.functional import cached_property

from rca.utils.filter import TabStyleFilter


class SchoolCentreExpertiseFilter(TabStyleFilter):
    """
    Custom TabStyleFilter class for use on StaffIndexPage, which presents combined
    filter options for filtering by "School", "Research Centre" or "Area of expertise",
    and can filter the queryset according to the selected options.
    """

    school_value_prefix = "s-"
    centre_value_prefix = "c-"
    expertise_value_prefix = "e-"

    def __init__(
        self, tab_title, school_queryset, centre_queryset, expertise_queryset, **kwargs
    ):
        super().__init__(tab_title, None, **kwargs)
        self.school_queryset = school_queryset
        self.centre_queryset = centre_queryset
        self.expertise_queryset = expertise_queryset
        # Trick template into displaying choices
        self.queryset = bool(
            self.school_queryset or self.centre_queryset or self.expertise_queryset
        )

    def apply(self, queryset, querydict):
        """
        Overrides TabStyleFilter.apply() to filter the queryset
        via several relationships.
        """
        self.querydict = querydict
        return queryset.filter(
            self.get_school_filter_q()
            | self.get_centre_filter_q()
            | self.get_expertise_filter_q()
        )

    def get_deprefixed_value_set(self, prefix):
        if not self.querydict:
            return set()
        return set(
            val[len(prefix) :]
            for val in self.querydict.getlist(self.name)
            if val.startswith(prefix)
        )

    @cached_property
    def selected_school_values(self):
        return self.get_deprefixed_value_set(self.school_value_prefix)

    @cached_property
    def selected_centre_values(self):
        return self.get_deprefixed_value_set(self.centre_value_prefix)

    @cached_property
    def selected_expertise_values(self):
        return self.get_deprefixed_value_set(self.expertise_value_prefix)

    @staticmethod
    def generate_prefixed_choices(
        queryset, prefix, selected_vals, value_field="slug", label_field="title"
    ):
        for val, label in queryset.values_list(value_field, label_field).distinct():
            yield {
                "id": f"{prefix}{val}",
                "title": label,
                "active": val in selected_vals,
            }

    def get_school_choices(self):
        return self.generate_prefixed_choices(
            self.school_queryset, self.school_value_prefix, self.selected_school_values
        )

    def get_centre_choices(self):
        return self.generate_prefixed_choices(
            self.centre_queryset, self.centre_value_prefix, self.selected_centre_values
        )

    def get_expertise_choices(self):
        return self.generate_prefixed_choices(
            self.expertise_queryset,
            self.expertise_value_prefix,
            self.selected_expertise_values,
        )

    @property
    def is_selected(self):
        if not self.querydict:
            return False
        return bool(self.querydict.get(self.name))

    def get_school_filter_q(self):
        if not self.selected_school_values:
            return Q()
        return Q(related_schools__page__slug__in=self.selected_school_values)

    def get_centre_filter_q(self):
        if not self.selected_centre_values:
            return Q()
        return Q(
            related_research_centre_pages__page__slug__in=self.selected_centre_values
        )

    def get_expertise_filter_q(self):
        if not self.selected_expertise_values:
            return Q()
        return Q(
            related_area_of_expertise__area_of_expertise__slug__in=self.selected_expertise_values
        )

    @cached_property
    def options(self):
        choices = list(self.get_school_choices())
        choices.extend(self.get_centre_choices())
        choices.extend(self.get_expertise_choices())
        choices.sort(key=lambda item: item["title"])
        return choices
