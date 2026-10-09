"""Compare regions by the make-up of their apprenticeships.

Regions are compared by shares within each region, never by raw counts, so a
large region does not rank higher just because it is large. The data set has
no population figures, so no per-capita rate is calculated. The location code
``z`` is the region "Outside of England and unknown". It is not a region of
England, so it is reported separately and never ranked with the nine regions.
The same letter is a suppression marker in value columns, which is why it is
only ever read here as a code.
"""

from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from apprenticeship_explorer.metrics import FILTERS
from apprenticeship_explorer.parse import Missing, parse_indicator_value
from apprenticeship_explorer.selector import select_cell
from apprenticeship_explorer.time_period import AcademicYear, normalise_time_period
from apprenticeship_explorer.window import DEFAULT_START, filter_to_window

OUTSIDE_ENGLAND = "z"
HIGHER = "Higher Apprenticeship"
REGION_DIMENSIONS = ("geographic_level", "region_code", *FILTERS)


@dataclass(frozen=True)
class RegionShare:
    """One region's share of its own starts that fall in one option.

    Attributes:
        code: The region's code, such as ``E12000007``.
        name: The region's name, such as ``London``.
        share: The percentage of the region's starts, or a ``Missing`` with
            its reason.
    """

    code: str
    name: str
    share: object


@dataclass(frozen=True)
class RegionalComparison:
    """The regions of England ranked for one year, with the outside region apart.

    Attributes:
        year: The academic year.
        regions: The nine regions of England, highest share first.
        outside: "Outside of England and unknown", reported separately.
    """

    year: AcademicYear
    regions: tuple[RegionShare, ...]
    outside: RegionShare


def regional_comparison(
    rows: Iterable[Mapping[str, str]],
    column: str = "apprenticeship_level",
    option: str = HIGHER,
    start: AcademicYear = DEFAULT_START,
) -> list[RegionalComparison]:
    """Rank regions by the share of their starts in one option, for each year.

    Args:
        rows: Data rows as read from the CSV, with every value as text.
        column: The filter that defines the share, such as
            ``apprenticeship_level``.
        option: The option whose share is compared, by default higher
            apprenticeships.
        start: The first academic year of the window.

    Returns:
        One comparison per year in the window, oldest first.
    """
    by_year = defaultdict(list)
    for row in filter_to_window(rows, start):
        if row["geographic_level"] == "Regional":
            by_year[normalise_time_period(row["time_period"])].append(row)
    comparisons = []
    for year, year_rows in sorted(by_year.items()):
        regions = dict.fromkeys((r["region_code"], r["region_name"]) for r in year_rows)
        shares = [_region_share(year_rows, code, name, column, option) for code, name in regions]
        inside = [s for s in shares if s.code != OUTSIDE_ENGLAND]
        outside = next(s for s in shares if s.code == OUTSIDE_ENGLAND)
        ranked = sorted(inside, key=lambda s: s.share, reverse=True)
        comparisons.append(RegionalComparison(year, tuple(ranked), outside))
    return comparisons


def _region_share(year_rows, code, name, column, option):
    """Return one region's share of its starts in an option.

    Args:
        year_rows: One year's regional rows.
        code: The region's code.
        name: The region's name.
        column: The filter that defines the share.
        option: The option whose share is wanted.

    Returns:
        The region's share, missing if the count or the total is suppressed.
    """
    base = {"geographic_level": "Regional", "region_code": code, **{f: "Total" for f in FILTERS}}
    total = parse_indicator_value(select_cell(year_rows, REGION_DIMENSIONS, base)["start_count"])
    cell = select_cell(year_rows, REGION_DIMENSIONS, {**base, column: option})
    count = parse_indicator_value(cell["start_count"])
    if isinstance(count, Missing):
        return RegionShare(code, name, count)
    if isinstance(total, Missing):
        return RegionShare(code, name, total)
    return RegionShare(code, name, 100 * count / total)