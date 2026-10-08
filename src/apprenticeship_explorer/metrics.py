"""Compute the figures the report shows from the published rows.

Every figure is read from a single row chosen with ``select_cell``, because
the published file already contains subtotals. Each measure is named by what
it counts. A start or an achievement is an event, and one learner can start
more than once, so no measure is ever described as a number of learners.
"""

from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from apprenticeship_explorer.parse import Missing, parse_indicator_value
from apprenticeship_explorer.selector import select_cell
from apprenticeship_explorer.time_period import AcademicYear, normalise_time_period
from apprenticeship_explorer.window import DEFAULT_START, filter_to_window

FILTERS = ("apprenticeship_level", "age_group", "age_youth_adult", "funding_type", "provider_type")
DIMENSIONS = ("geographic_level", *FILTERS)
NATIONAL_TOTAL = {"geographic_level": "National", **{f: "Total" for f in FILTERS}}
FUNDING_START = AcademicYear(2020)
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
    mix = []
    for year, year_rows in _national_years(rows, start):
        total_row = select_cell(year_rows, DIMENSIONS, NATIONAL_TOTAL)
        total = parse_indicator_value(total_row["start_count"])
        options = dict.fromkeys(r[column] for r in year_rows if r[column] != "Total")
        shares = {}
        for option in options:
            cell = _option_cell(year_rows, column, option, nested_in)
            shares[option] = _share(parse_indicator_value(cell["start_count"]), total)
        mix.append(YearShares(year, shares))
    return mix


def level_mix(rows: Iterable[Mapping[str, str]]) -> list[YearShares]:
    """Return each apprenticeship level's share of national starts, by year.

    Args:
        rows: Data rows as read from the CSV, with every value as text.

    Returns:
        One entry per year in the analysis window, oldest first.
    """
    return share_mix(rows, "apprenticeship_level")


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
    return share_mix(rows, "age_group", nested_in="age_youth_adult")


def _national_years(rows, start):
    """Group the window's national rows by academic year, oldest first.

    Args:
        rows: Data rows as read from the CSV.
        start: The first academic year of the window.

    Returns:
        Pairs of each academic year and its national rows.
    """
    by_year = defaultdict(list)
    for row in filter_to_window(rows, start):
        if row["geographic_level"] == "National":
            by_year[normalise_time_period(row["time_period"])].append(row)
    return sorted(by_year.items())


def _option_cell(year_rows, column, option, nested_in):
    """Select the one row for an option, with every other filter at ``Total``.

    Args:
        year_rows: One year's national rows.
        column: The filter being broken down.
        option: The option wanted, such as ``19 to 24``.
        nested_in: A filter whose value goes with the option, if any.

    Returns:
        The single matching row.
    """
    selection = {**NATIONAL_TOTAL, column: option}
    if nested_in:
        others = [f for f in FILTERS if f not in (column, nested_in)]
        parents = {
            r[nested_in]
            for r in year_rows
            if r[column] == option and all(r[f] == "Total" for f in others)
        }
        if len(parents) == 1:
            selection[nested_in] = parents.pop()
    return select_cell(year_rows, DIMENSIONS, selection)


def _share(count, total):
    """Return a count as a percentage of a total, keeping a missing value missing.

    Args:
        count: The option's count, or a ``Missing``.
        total: The year's total, or a ``Missing``.

    Returns:
        The percentage, or whichever value is missing, so its reason survives.
    """
    if isinstance(count, Missing):
        return count
    if isinstance(total, Missing):
        return total
    return 100 * count / total


def funding_mix(rows: Iterable[Mapping[str, str]]) -> list[YearShares]:
    """Return levy-funded and other starts as shares of national starts, by year.

    The mix starts in 2020/21. A minor amendment to how starts supported by
    levy funds are counted was applied for 2019/20, and a further one from
    2020/21, so 2020/21 is the first year counted on the current basis.

    Args:
        rows: Data rows as read from the CSV, with every value as text.

    Returns:
        One entry per year from 2020/21 to the last complete year.
    """
    # Deliberately not implemented yet. The tests are written first.
    raise NotImplementedError