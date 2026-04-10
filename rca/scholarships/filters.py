from rca.utils.filter import TabStyleFilter


class FeeStatusFilter:
    name = "fee-status"

    def __init__(self):
        self.tab_title = "Fee Status"
        self.querydict = None
        self.queryset = (
            False  # no tab/takeover panel — toggle switch handles this filter
        )

    # The query parameter values are `uk` and `international`
    # and the DB slugs are `home-fee-status` and `overseas-fee-status`.
    SLUG_MAP = {
        "uk": "home-fee-status",
        "international": "overseas-fee-status",
    }

    def apply(self, queryset, querydict):
        self.querydict = querydict
        fee_status = querydict.get(self.name)
        db_slug = self.SLUG_MAP.get(fee_status)
        if db_slug:
            return queryset.filter(fee_statuses__slug=db_slug)
        return queryset

    @property
    def selected_value(self):
        if not self.querydict:
            return None
        return self.querydict.get(self.name)

    @property
    def is_selected(self):
        return bool(self.selected_value)

    @property
    def filter_name(self):
        return self.name

    @property
    def options(self):
        yield from self

    def __iter__(self):
        from .models import ScholarshipFeeStatus

        for fee_status in ScholarshipFeeStatus.objects.all():
            yield {
                "id": fee_status.slug,
                "title": fee_status.title,
                "active": self.selected_value == fee_status.slug,
            }

    def get_active_filters(self):
        return [option for option in self.options if option["active"]]


class ProgrammeTabStyleFilter(TabStyleFilter):
    def __iter__(self):
        # iter is overridden here so we can populate a title for the filter
        # value consisting of programme name and degree level.
        # E.G [architecture] [ma]

        for item in self.queryset.values_list(
            self.option_value_field, self.option_label_field, "degree_level__title"
        ).order_by(self.option_label_field):
            label = item[0]
            title = item[1]
            suffix = item[2]
            yield dict(
                id=label,
                title=title,
                suffix=suffix,
                active=bool(label in self.selected_values),
            )
