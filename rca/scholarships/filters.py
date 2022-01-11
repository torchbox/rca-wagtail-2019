from rca.utils.filter import TabStyleFilter


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
