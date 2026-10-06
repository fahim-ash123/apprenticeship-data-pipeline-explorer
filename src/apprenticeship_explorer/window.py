"""Limit the analysis to complete academic years.

The data set describes itself as full-year final data plus the latest data
reported to date, so its latest period is always partial. Footnote 12 confirms
this for 2025/26, which covers August to April only. A partial year would look
like a fall in starts, so the latest period is left out by rule. No year is
written into the code, which means the rule keeps working when the publisher
adds a new year.
"""

from collections.abc import Iterable, Mapping

from apprenticeship_explorer.time_period import AcademicYear

DEFAULT_START = AcademicYear(2017)


class EmptyWindowError(ValueError):
    """Raised when no complete academic year falls inside the window."""


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

    Raises:
        EmptyWindowError: If there are no periods, or none is complete and on
            or after ``start``.
    """
    distinct = set(periods)
    latest = max(distinct)
    return tuple(sorted(year for year in distinct if start <= year < latest))


def filter_to_window(
    rows: Iterable[Mapping[str, str]], start: AcademicYear = DEFAULT_START
) -> list[Mapping[str, str]]:
    """Keep only the rows whose time period is inside the analysis window.

    The window is worked out from the rows themselves, so the latest period in
    the data is the one left out.

    Args:
        rows: The data rows, each with a ``time_period`` value as read from
            the CSV, such as ``202122``.
        start: The first academic year of the window. Defaults to 2017/18.

    Returns:
        The rows inside the window, unchanged and in their original order.

    Raises:
        EmptyWindowError: If no complete year is on or after ``start``.
    """
    # Deliberately not implemented yet. The tests are written first.
    raise NotImplementedError