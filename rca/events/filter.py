import datetime

from django.db import models


class PastFutureChoices(models.TextChoices):
    FUTURE = "future", "Upcoming"
    PAST = "past", "Past"


TODAY = datetime.date.today()


class PastOrFutureFilter:
    name = "tense"

    def __init__(
        self,
        tab_title,
    ):
        self.tab_title = tab_title
        self.querydict = None
        self.queryset = True

    def apply(self, queryset, querydict):
        """
        Return a new queryset, filtered according to the values
        present in the supplied QueryDict (which will typically be
        ``request.GET`` or ``request.POST``)
        """
        self.querydict = querydict
        if self.selected_value == PastFutureChoices.PAST:
            return queryset.filter(start_date__lt=TODAY)
        if self.selected_value == PastFutureChoices.FUTURE:
            return queryset.filter(end_date__gte=TODAY).order_by("start_date")
        # Modify the queryset if no filters are passed in here and show only
        # upcoming dates.
        queryset = queryset.filter(end_date__gte=TODAY).order_by("start_date")
        return queryset

    @property
    def selected_value(self):
        value = self.querydict.get(self.name)
        if value in PastFutureChoices.values:
            return value
        return None

    @property
    def is_selected(self):
        return self.selected_value is not None

    @property
    def filter_name(self):
        # to match template usage
        return self.name

    def get_active_filters(self):
        return [option for option in self.options if option["active"]]

    def __iter__(self):
        for value, label in PastFutureChoices.choices:
            yield dict(id=value, title=label, active=bool(value == self.selected_value))

    @property
    def options(self):
        yield from self
