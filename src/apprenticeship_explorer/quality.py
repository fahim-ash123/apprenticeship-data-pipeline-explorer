"""Profile how much of the published data is suppressed or unavailable.

Four markers stand in for numbers (footnote 8): ``c`` for suppressed, ``x``
for unavailable, ``z`` for not applicable and ``low`` for a percentage below
0.5%. The profile counts each marker by indicator and by breakdown, so a
reader can judge which questions the data can answer. ``low`` is defined only
for percentages, so the profile also counts how often it appears in the count
columns, where the footnote does not explain it.
"""

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from apprenticeship_explorer.metrics import FILTERS

MARKERS = ("c", "low", "x", "z")
COUNT_COLUMNS = ("start_count", "achievement_count", "participation_count")
INDICATORS = (*COUNT_COLUMNS, "starts_percent", "achievements_percent")


@dataclass(frozen=True)
class QualityProfile:
    """How often each marker appears, and how many rows are pre-computed subtotals.

    Attributes:
        rows_loaded: How many rows were read.
        markers_by_indicator: For each indicator column, how many cells hold
            each marker.
        markers_by_breakdown: For each breakdown, such as
            ``apprenticeship_level+funding_type``, how many cells hold each
            marker.
        low_in_count_columns: How many count cells hold ``low``.
        subtotal_rows: How many rows have at least one filter at ``Total``.
            These are pre-computed subtotals, so they are never added together.
    """

    rows_loaded: int
    markers_by_indicator: Mapping[str, Counter]
    markers_by_breakdown: Mapping[str, Counter]
    low_in_count_columns: int
    subtotal_rows: int

    @property
    def suppressed_cells_by_marker(self) -> Counter:
        """Every marked cell in the data, counted by marker."""
        return sum(self.markers_by_indicator.values(), Counter())


def breakdown(row: Mapping[str, str]) -> str:
    """Name the filters a row is broken down by, such as ``apprenticeship_level``.

    An age group row also carries its matching youth or adult value, so when
    ``age_group`` is broken down, ``age_youth_adult`` is not counted again.

    Args:
        row: One data row.

    Returns:
        The broken-down filters joined with ``+``, or ``Total`` if none are.
    """
    filters = [f for f in FILTERS if row[f] != "Total"]
    if "age_group" in filters and "age_youth_adult" in filters:
        filters.remove("age_youth_adult")
    return "+".join(filters) or "Total"


def profile(rows: Iterable[Mapping[str, str]]) -> QualityProfile:
    """Count the markers in every indicator cell of the data.

    Args:
        rows: Data rows as read from the CSV, with every value as text.

    Returns:
        The profile of the rows.
    """
    by_indicator = {column: Counter() for column in INDICATORS}
    by_breakdown = defaultdict(Counter)
    loaded = low_in_counts = subtotals = 0
    for row in rows:
        loaded += 1
        subtotals += any(row[f] == "Total" for f in FILTERS)
        for column in INDICATORS:
            value = row[column].strip()
            if value in MARKERS:
                by_indicator[column][value] += 1
                by_breakdown[breakdown(row)][value] += 1
                low_in_counts += value == "low" and column in COUNT_COLUMNS
    return QualityProfile(loaded, by_indicator, dict(by_breakdown), low_in_counts, subtotals)