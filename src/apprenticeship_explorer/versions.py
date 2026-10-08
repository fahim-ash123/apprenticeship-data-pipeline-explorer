"""Parse, order and compare data set versions.

The API writes versions with two parts, such as ``2.0``, or three, such as
``2.0.2``, and does not return them in order. Version 1.0 comes back after
2.0 and before 1.0.1. Sorting the strings as text would also put ``1.10``
before ``1.9``. Each version is therefore parsed into numbers before it is
compared, with a missing patch number counted as zero.
"""

from collections.abc import Iterable
from dataclasses import dataclass


class InvalidVersionError(ValueError):
    """Raised when a value is not a two-part or three-part version number."""


@dataclass(frozen=True, order=True)
class Version:
    """A data set version, compared by its major, minor and patch numbers.

    Attributes:
        major: The major number, which changes when the structure breaks.
        minor: The minor number.
        patch: The patch number, zero when the API leaves it out.
    """

    major: int
    minor: int
    patch: int = 0

    def __str__(self) -> str:
        """Return the version as the API writes it, leaving out a zero patch."""
        if self.patch:
            return f"{self.major}.{self.minor}.{self.patch}"
        return f"{self.major}.{self.minor}"


def parse_version(raw: str) -> Version:
    """Convert a version string into a comparable ``Version``.

    Args:
        raw: The version as the API writes it, such as ``2.0`` or ``2.0.2``.

    Returns:
        The parsed version.

    Raises:
        InvalidVersionError: If the value is not two or three numbers
            separated by full stops.
    """
    # Deliberately not implemented yet. The tests are written first.
    raise NotImplementedError


def sort_versions(raw_versions: Iterable[str]) -> list[Version]:
    """Return versions in order from oldest to newest, whatever order they arrive in.

    Args:
        raw_versions: Version strings as the API returned them.

    Returns:
        The parsed versions, oldest first.
    """
    raise NotImplementedError


def latest_version(raw_versions: Iterable[str]) -> Version:
    """Return the newest version.

    Args:
        raw_versions: Version strings as the API returned them.

    Returns:
        The highest version by number, not the first one listed.
    """
    raise NotImplementedError