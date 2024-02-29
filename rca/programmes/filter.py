from rca.utils.filter import TabStyleFilter


class ProgrammeStyleFilter(TabStyleFilter):
    """
    Custom TabStyleFilter class for ProgrammePages since we want to display the
    string representation of the programme instead of just the title.
    """

    def __iter__(self):
        values = [
            (getattr(programme, self.option_value_field), str(programme))
            for programme in self.queryset.order_by(self.option_value_field)
        ]

        for value, label in values:
            yield dict(
                id=value, title=label, active=bool(value in self.selected_values)
            )
