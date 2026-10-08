"""Compute the figures the report shows from the published rows.

Every figure is read from a single row chosen with ``select_cell``, because
the published file already contains subtotals. Each measure is named by what
it counts. A start or an achievement is an event, and one learner can start
more than once, so no measure is ever described as a number of learners.
"""

from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from apprenticeship_explorer.parse import parse_indicator_value
from apprenticeship_explorer.selector import select_cell
from apprenticeship_explorer.time_period import AcademicYear, normalise_time_period
from apprenticeship_explorer.window import DEFAULT_START, filter_to_window

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
            ``start_count``. A suppressed or unavailable value is a ``Missing``
            that keeps its reason, never a zero.
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
    by_year = defaultdict(list)
    for row in filter_to_window(rows):
        by_year[normalise_time_period(row["time_period"])].append(row)
    trend = []
    for year in sorted(by_year):
        row = select_cell(by_year[year], DIMENSIONS, NATIONAL_TOTAL)
        values = {column: parse_indicator_value(row[column]) for column in MEASURES}
        trend.append(YearFigures(year, values))
    return trend

@dataclass(frozen=True)
class YearShares:
    """Each option's share of all starts in one academic year.

    Attributes:
        year: The academic year.
        shares: Each option's percentage of the year's total starts, keyed by
            the option's label, such as ``Higher Apprenticeship``. A share
            whose count or total is suppressed is a ``Missing`` with its
            reason.
    """

    year: AcademicYear
    shares: Mapping[str, object]


def share_mix(
    rows: Iterable[Mapping[str, str]],
    column: str,
    start: AcademicYear = DEFAULT_START,
    nested_in: str | None = None,
) -> list[YearShares]:
    """Return each option of one filter as a percentage of national starts, by year.

    The denominator is the published national total, not the sum of the
    options, because the published counts are rounded to the nearest 10.

    Args:
        rows: Data rows as read from the CSV, with every value as text.
        column: The filter to break starts down by, such as ``age_group``.
        start: The first academic year of the window.
        nested_in: A filter whose value is fixed by ``column`` instead of being
            ``Total``. Each age group row carries its matching under 19 or
            19 plus value in ``age_youth_adult``.

    Returns:
        One entry per year in the window, oldest first.
    """
    # Deliberately not implemented yet. The tests are written first.
    raise NotImplementedError


def level_mix(rows: Iterable[Mapping[str, str]]) -> list[YearShares]:
    """Return each apprenticeship level's share of national starts, by year.

    Args:
        rows: Data rows as read from the CSV, with every value as text.

    Returns:
        One entry per year in the analysis window, oldest first.
    """
    raise NotImplementedError


def age_mix(rows: Iterable[Mapping[str, str]]) -> list[YearShares]:
    """Return each age group's share of national starts, by year.

    Age is age at the start of the apprenticeship. The age group rows sit
    under the youth or adult split, so ``19 to 24`` has ``age_youth_adult`` set
    to ``19 plus``, not ``Total``.

    Args:
        rows: Data rows as read from the CSV, with every value as text.

    Returns:
        One entry per year in the analysis window, oldest first.
    """
    raise NotImplementedError