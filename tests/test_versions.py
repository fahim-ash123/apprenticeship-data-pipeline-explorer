"""Tests for parsing and ordering data set versions.

The recorded version list in ``tests/fixtures/versions.json`` is the real
response from the API. It returns the versions as 2.0.2, 2.0.1, 2.0, 1.0,
1.0.1 and 1.0.2, which is neither newest first nor oldest first.
"""

import json
from pathlib import Path

import pytest

from apprenticeship_explorer.versions import (
    InvalidVersionError,
    Version,
    latest_version,
    parse_version,
    sort_versions,
)

FIXTURES = Path(__file__).parent / "fixtures"


def recorded_versions():
    """Return the version strings in the order the API returned them."""
    reply = json.loads((FIXTURES / "versions.json").read_text())
    return [entry["version"] for entry in reply["results"]]


def test_three_part_version_parses():
    """A patch release such as 2.0.2 keeps all three numbers."""
    assert parse_version("2.0.2") == Version(2, 0, 2)


def test_two_part_version_parses_with_a_zero_patch():
    """A major release such as 2.0 is written with two parts."""
    assert parse_version("2.0") == Version(2, 0, 0)


def test_two_part_and_three_part_forms_are_equal():
    """2.0 and 2.0.0 are the same version."""
    assert parse_version("2.0") == parse_version("2.0.0")


def test_version_displays_as_the_api_writes_it():
    """A zero patch is left out, so 2.0 stays 2.0 in the report."""
    assert [str(parse_version(raw)) for raw in ("2.0", "2.0.2")] == ["2.0", "2.0.2"]


@pytest.mark.parametrize(
    "raw", ["", "2", "2.0.0.1", "v2.0", "2.x", "2.0.", "-1.0", "\uff12.0"]
)
def test_invalid_versions_raise_an_error(raw):
    """Anything that is not two or three numbers separated by full stops is rejected.

    The last case is 2.0 with a full-width digit, which Python's ``int`` would
    otherwise accept.
    """
    with pytest.raises(InvalidVersionError):
        parse_version(raw)


def test_recorded_versions_sort_into_order():
    """The API's mixed order becomes oldest to newest."""
    assert [str(v) for v in sort_versions(recorded_versions())] == [
        "1.0",
        "1.0.1",
        "1.0.2",
        "2.0",
        "2.0.1",
        "2.0.2",
    ]


def test_versions_sort_by_number_not_as_text():
    """As text, 1.10 would come before 1.9. As numbers it comes after."""
    assert [str(v) for v in sort_versions(["1.10", "1.9", "1.2"])] == ["1.2", "1.9", "1.10"]


def test_latest_version_is_found_from_the_recorded_list():
    """The latest is 2.0.2, found by number, not by its place in the response."""
    assert latest_version(recorded_versions()) == Version(2, 0, 2)


def test_latest_version_does_not_depend_on_response_order():
    """Reversing the response does not change which version is latest."""
    assert latest_version(reversed(recorded_versions())) == Version(2, 0, 2)