from collections import defaultdict

from rca.utils.filter import TabStyleFilter


class ProgrammeTabStyleFilter(TabStyleFilter):
    def __iter__(self):
        # iter is overridden here so we can populate a title for the filter
        # value consisting of programme name and degree level(s).
        # E.G [architecture] [ma, mfa]

        degree_level_titles = defaultdict(list)
        for page_id, level_title in self.queryset.values_list(
            "id", "degree_levels__level__title"
        ):
            if level_title:
                degree_level_titles[page_id].append(level_title)

        for page_id, label, title in self.queryset.values_list(
            "id", self.option_value_field, self.option_label_field
        ).order_by(self.option_label_field):
            yield dict(
                id=label,
                title=title,
                suffix=", ".join(degree_level_titles[page_id]),
                active=bool(label in self.selected_values),
            )
