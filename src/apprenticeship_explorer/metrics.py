"""Compute the figures the report shows from the published rows.

Every figure is read from a single row chosen with ``select_cell``, because
the published file already contains subtotals. Each measure is named by what
it counts. A start or an achievement is an event, and one learner can start
more than once, so no measure is ever described as a number of learners.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from apprenticeship_explorer.time_period import AcademicYear

FILTERS = ("apprenticeship_level", "age_group", "age_youth_adult", "funding_type", "provider_type")
DIMENSIONS = ("geographic_level", *FILTERS)
NATIONAL_TOTAL = {"geographic_level": "National", **{f: "Total" for f in FILTERS}}
MEASURES = {
    "start_count": "Starts",
    "achievement_count": "Achievements",
    "participation_count": "Participation",
}


@dataclass(frozen=True)
class YearFigures:
    """The national figures for one academic year.

    Attributes:
        year: The academic year.
        values: Each measure's value, keyed by its indicator column, such as
            ``start_count``.
    """

    year: AcademicYear
    values: Mapping[str, object]


def national_trend(rows: Iterable[Mapping[str, str]]) -> list[YearFigures]:
    """Return national starts, achievements and participation for each complete year.

    Args:
        rows: Data rows as read from the CSV, with every value as text.

    Returns:
        One entry per year in the analysis window, oldest first.
    """
    # Deliberately not implemented yet. The tests are written first.
    raise NotImplementedError