"""Compare regions by the make-up of their apprenticeships.

Regions are compared by shares within each region, never by raw counts, so a
large region does not rank higher just because it is large. The data set has
no population figures, so no per-capita rate is calculated. The location code
``z`` is the region "Outside of England and unknown". It is not a region of
England, so it is reported separately and never ranked with the nine regions.
The same letter is a suppression marker in value columns, which is why it is
only ever read here as a code.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from apprenticeship_explorer.metrics import FILTERS
from apprenticeship_explorer.time_period import AcademicYear
from apprenticeship_explorer.window import DEFAULT_START

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
    # Deliberately not implemented yet. The tests are written first.
    raise NotImplementedError