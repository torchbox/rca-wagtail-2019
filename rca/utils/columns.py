from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from wagtail.admin.ui.tables import Column


def insert_columns(
    *,
    source_columns: "Sequence[Column]",
    insert_before_column_ref: str,
    columns_to_insert: "Sequence[Column]",
) -> "list[Column]":
    """
    Returns a copy of the given source column, with new column inserted before
    a given column reference in that copy.

    The `insert_before_column_ref` parameter is a string that identifies the column,
    either by its `name` or by its `label`.
    """

    new_columns: "list[Column]" = []

    for column in source_columns:
        column_heading_values = (
            getattr(column, "name", None),
            getattr(column, "label", None),
        )
        if insert_before_column_ref in column_heading_values:
            new_columns.extend(columns_to_insert)
        new_columns.append(column)

    return new_columns
