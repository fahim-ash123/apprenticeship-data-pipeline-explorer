"""Select single cells from the published data without double counting.

The published file already contains subtotal rows. A row whose filter value
is ``Total`` is the sum of the rows broken down by that filter, so adding up
every matching row counts the same apprenticeships several times. A figure is
therefore always read from exactly one row, chosen by giving a value for every
dimension, with ``Total`` for a dimension that is not broken down.
"""

from collections.abc import Iterable, Mapping, Sequence


class SelectionError(LookupError):
    """Raised when a selection does not identify exactly one row."""


class IncompleteSelectionError(SelectionError):
    """Raised when a selection leaves out a dimension or names an unknown one."""


class NoMatchingRowError(SelectionError):
    """Raised when no row matches the selection."""


class AmbiguousSelectionError(SelectionError):
    """Raised when more than one row matches the selection."""


def select_cell(
    rows: Iterable[Mapping[str, str]],
    dimensions: Sequence[str],
    selection: Mapping[str, str],
) -> Mapping[str, str]:
    """Return the one row that matches a value for every dimension.

    Args:
        rows: The data rows, with every value as text, as read from the CSV.
        dimensions: The columns that together identify a row, such as
            ``time_period`` and ``age_group``.
        selection: The value wanted for each dimension. Use ``Total`` for a
            dimension that is not broken down.

    Returns:
        The single matching row.

    Raises:
        IncompleteSelectionError: If the selection leaves out a dimension or
            names a column that is not a dimension.
        NoMatchingRowError: If no row matches.
        AmbiguousSelectionError: If more than one row matches.
    """
    matches = [
        row for row in rows if all(row[column] == value for column, value in selection.items())
    ]
    if not matches:
        raise NoMatchingRowError(f"No row matches {dict(selection)!r}")
    if len(matches) > 1:
        raise AmbiguousSelectionError(f"{len(matches)} rows match {dict(selection)!r}")
    return matches[0]