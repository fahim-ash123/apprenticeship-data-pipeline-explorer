"""Parse indicator values from the Explore Education Statistics CSV.

The published CSV mixes numbers with symbols that explain why a value is
missing. If those symbols were treated as zero, or simply dropped, the meaning
of the data would change without any warning. Each symbol is therefore kept as
a typed missing value that records why it was withheld.

Footnote 8 of the data set defines ``low`` only for percentages, but it also
appears in the count columns, so its reason is worded to cover both.
"""

import math
from dataclasses import dataclass

# Each published marker and the reason it stands for.
MARKER_REASONS = {
    "c": "suppressed to protect confidentiality",
    "x": "not available",
    "z": "not applicable",
    "low": "below the publication threshold",
}


@dataclass(frozen=True)
class Missing:
    """An indicator value that was not published.

    Attributes:
        marker: The symbol as it appears in the CSV, for example ``c``.
        reason: A plain explanation of why the value is missing.
    """

    marker: str
    reason: str


class UnrecognisedValueError(ValueError):
    """Raised when an indicator value is neither a number nor a known marker."""


def parse_indicator_value(raw: str) -> int | float | Missing:
    """Convert one raw indicator value into a number or a Missing marker.

    Markers are matched exactly, so ``C`` is rejected. The published symbols
    are all lower case, and accepting variants could hide a problem in the
    source data.

    Args:
        raw: The value exactly as read from the CSV.

    Returns:
        An ``int`` for whole numbers such as counts, a ``float`` for decimals
        such as percentages, or a ``Missing`` value for a published marker.

    Raises:
        UnrecognisedValueError: If the value is empty, not a number, not finite,
            or not one of the known markers.
    """
    value = raw.strip()
    if value in MARKER_REASONS:
        return Missing(marker=value, reason=MARKER_REASONS[value])

    # Try a whole number first so that counts stay as integers.
    try:
        return int(value)
    except ValueError:
        pass

    try:
        number = float(value)
    except ValueError:
        raise UnrecognisedValueError(f"Unrecognised indicator value: {raw!r}") from None

    # float() accepts 'nan' and 'inf', which are never real published figures.
    if not math.isfinite(number):
        raise UnrecognisedValueError(f"Unrecognised indicator value: {raw!r}")
    return number