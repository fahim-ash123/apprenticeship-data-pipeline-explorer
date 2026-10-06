"""Limit the analysis to complete academic years.

The data set describes itself as full-year final data plus the latest data
reported to date, so its latest period is always partial. Footnote 12 confirms
this for 2025/26, which covers August to April only. A partial year would look
like a fall in starts, so the latest period is left out by rule. No year is
written into the code, which means the rule keeps working when the publisher
adds a new year.
"""

from collections.abc import Iterable

from apprenticeship_explorer.time_period import AcademicYear

DEFAULT_START = AcademicYear(2017)


def complete_periods(
    periods: Iterable[AcademicYear], start: AcademicYear = DEFAULT_START
) -> tuple[AcademicYear, ...]:
    """Return the complete academic years from ``start`` onwards.

    Args:
        periods: The academic years in the data, in any order and with repeats
            allowed.
        start: The first academic year of the window. Defaults to 2017/18.

    Returns:
        Each year from ``start`` up to, but not including, the latest year,
        in chronological order.
    """
    distinct = set(periods)
    latest = max(distinct)
    return tuple(sorted(year for year in distinct if start <= year < latest))