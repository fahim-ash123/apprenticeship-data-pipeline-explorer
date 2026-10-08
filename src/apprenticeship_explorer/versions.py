"""Parse, order and compare data set versions.

The API writes versions with two parts, such as ``2.0``, or three, such as
``2.0.2``, and does not return them in order. Version 1.0 comes back after
2.0 and before 1.0.1. Sorting the strings as text would also put ``1.10``
before ``1.9``. Each version is therefore parsed into numbers before it is
compared, with a missing patch number counted as zero.

The version type does not reliably signal structural change either. Patch
release 1.0.1 added the ``age_youth_adult`` filter, so the structure of two
versions is compared directly instead of trusted from the version number.
"""

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

VERSION_FORM = re.compile(r"([0-9]+)\.([0-9]+)(?:\.([0-9]+))?")


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
    match = VERSION_FORM.fullmatch(raw.strip())
    if not match:
        raise InvalidVersionError(f"Unrecognised version: {raw!r}")
    major, minor, patch = match.groups(default="0")
    return Version(int(major), int(minor), int(patch))


def sort_versions(raw_versions: Iterable[str]) -> list[Version]:
    """Return versions in order from oldest to newest, whatever order they arrive in.

    Args:
        raw_versions: Version strings as the API returned them.

    Returns:
        The parsed versions, oldest first.
    """
    return sorted(parse_version(raw) for raw in raw_versions)


def latest_version(raw_versions: Iterable[str]) -> Version:
    """Return the newest version.

    Args:
        raw_versions: Version strings as the API returned them.

    Returns:
        The highest version by number, not the first one listed.
    """
    return sort_versions(raw_versions)[-1]


@dataclass(frozen=True)
class SchemaChanges:
    """The filters and indicators added or removed between two versions.

    Each collection holds column names, such as ``age_youth_adult``.

    Attributes:
        added_filters: Filters in the newer version only.
        removed_filters: Filters in the older version only.
        added_indicators: Indicators in the newer version only.
        removed_indicators: Indicators in the older version only.
    """

    added_filters: frozenset[str]
    removed_filters: frozenset[str]
    added_indicators: frozenset[str]
    removed_indicators: frozenset[str]

    @property
    def has_changes(self) -> bool:
        """Whether anything was added or removed."""
        return bool(
            self.added_filters
            or self.removed_filters
            or self.added_indicators
            or self.removed_indicators
        )


def compare_schemas(older: Mapping[str, Any], newer: Mapping[str, Any]) -> SchemaChanges:
    """Report the filters and indicators added or removed between two versions.

    Args:
        older: The ``/meta`` response for the earlier version.
        newer: The ``/meta`` response for the later version.

    Returns:
        The differences, compared by column name.
    """
    # Deliberately not implemented yet. The tests are written first.
    raise NotImplementedError