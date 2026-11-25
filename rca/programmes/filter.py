from rca.utils.filter import TabStyleFilter


class ProgrammeStyleFilter(TabStyleFilter):
    """
    Custom TabStyleFilter class for ProgrammePages since we want to display the
    string representation of the programme instead of just the title.
    """

    def __iter__(self):
        rows = list(
            self.queryset.order_by(self.option_value_field).values_list(
                "pk", self.option_value_field
            )
        )
        titles = self.queryset.model.full_titles([pk for pk, _ in rows])

        for pk, value in rows:
            yield dict(
                id=value, title=titles[pk], active=bool(value in self.selected_values)
            )
