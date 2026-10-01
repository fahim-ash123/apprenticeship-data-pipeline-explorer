"""Parse indicator values from the Explore Education Statistics CSV.

The published CSV mixes numbers with symbols that explain why a value is
missing. If those symbols were treated as zero, or simply dropped, the meaning
of the data would change without any warning. Each symbol is therefore kept as
a typed missing value that records why it was withheld.
"""

from dataclasses import dataclass


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

    Args:
        raw: The value exactly as read from the CSV.

    Returns:
        An ``int`` for whole numbers such as counts, a ``float`` for decimals
        such as percentages, or a ``Missing`` value for a published marker.

    Raises:
        UnrecognisedValueError: If the value is empty, not a number, not finite,
            or not one of the known markers.
    """
    # Deliberately not implemented yet. The tests are written first.
    raise NotImplementedError