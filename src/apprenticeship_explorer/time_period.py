"""Normalise academic year time periods from the Explore Education Statistics API.

The API writes the same academic year in three ways. The CSV uses ``202122``,
the metadata ``period`` field uses ``2021/2022`` and the metadata ``label``
field uses ``2021/22``. Data from different endpoints only joins correctly if
all three become one value, so each is converted to an ``AcademicYear``.
"""

import re
from dataclasses import dataclass

# [0-9], not \d, because \d also matches non-ASCII digits.
CSV_FORM = re.compile(r"([0-9]{4})([0-9]{2})")
PERIOD_FORM = re.compile(r"([0-9]{4})/([0-9]{4})")
LABEL_FORM = re.compile(r"([0-9]{4})/([0-9]{2})")


@dataclass(frozen=True)
class AcademicYear:
    """An academic year, identified by the calendar year it starts in.

    Attributes:
        start_year: The calendar year the academic year starts in, for example
            2021 for 2021/22.
    """

    start_year: int

    @property
    def label(self) -> str:
        """The year in the published label form, for example ``2021/22``."""
        return f"{self.start_year}/{(self.start_year + 1) % 100:02d}"

    def __str__(self) -> str:
        """Return the published label form."""
        return self.label


class InvalidTimePeriodError(ValueError):
    """Raised when a value is not a recognised form of an academic year."""


def normalise_time_period(raw: str) -> AcademicYear:
    """Convert one raw academic year into an ``AcademicYear``.

    Args:
        raw: The time period as it appears in the CSV or the metadata, such as
            ``202122``, ``2021/2022`` or ``2021/22``.

    Returns:
        The academic year the value represents.

    Raises:
        InvalidTimePeriodError: If the value is not one of the three forms, or
            its two years are not consecutive.
    """
    value = raw.strip()
    if match := PERIOD_FORM.fullmatch(value):
        start, end = int(match[1]), int(match[2])
        consecutive = end == start + 1
    elif match := CSV_FORM.fullmatch(value) or LABEL_FORM.fullmatch(value):
        start, end = int(match[1]), int(match[2])
        consecutive = end == (start + 1) % 100
    else:
        raise InvalidTimePeriodError(f"Unrecognised time period: {raw!r}")

    if not consecutive:
        raise InvalidTimePeriodError(f"Years are not consecutive: {raw!r}")
    return AcademicYear(start_year=start)