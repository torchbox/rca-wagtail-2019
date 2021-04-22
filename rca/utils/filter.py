from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.text import slugify


class TabStyleFilter:
    def __init__(
        self,
        tab_title,
        queryset,
        name=None,
        option_label_field=None,
        option_value_field=None,
        filter_by=None,
    ):
        self.tab_title = tab_title
        self.queryset = queryset
        self.name = name or slugify(tab_title)
        self.option_label_field = option_label_field or "title"
        self.option_value_field = option_value_field or "pk"
        self.filter_by = filter_by
        # This will be set when 'apply_filters()' is called
        self.querydict = None

    def apply(self, queryset, querydict):
        """
        Return a new queryset, filtered according to the values
        present in the supplied QueryDict (which will typically be
        ``request.GET`` or ``request.POST``)
        """
        self.querydict = querydict
        selected = self.selected_values
        if not selected:
            return queryset
        filter_q = self.get_filter_q()
        return queryset.filter(filter_q)

    def get_selected_queryset(self):
        if not self.querydict:
            return self.queryset.none()
        vals = set(self.querydict.getlist(self.name))
        if not vals:
            return self.queryset.none()
        kwargs = {f"{self.option_value_field}__in": vals}
        return self.queryset.filter(**kwargs)

    @cached_property
    def selected_values(self):
        return (
            self.get_selected_queryset()
            .values_list(self.option_value_field, flat=True)
            .distinct()
        )

    def get_filter_q(self):
        if isinstance(self.filter_by, str):
            filter_clauses = (self.filter_by,)
        else:
            filter_clauses = tuple(self.filter_by)
        filters = Q()  # Start with empty Q
        for fc in filter_clauses:
            kwargs = {fc: self.selected_values}
            filters |= Q(**kwargs)
        return filters

    @property
    def is_selected(self):
        return bool(self.selected_values)

    @property
    def filter_name(self):
        # to match template usage
        return self.name

    def get_active_filters(self):
        return [option for option in self.options if option["active"]]

    def __iter__(self):
        for value, label in self.queryset.values_list(
            self.option_value_field, self.option_label_field
        ).order_by(self.option_label_field):
            # would be nicer to user 'value' and 'label' as
            # keys here, but the 'id'/'title' combo seems
            # to be established already
            yield dict(
                id=value, title=label, active=bool(value in self.selected_values)
            )

    @property
    def options(self):
        yield from self
