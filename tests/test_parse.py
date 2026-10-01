"""Tests for parsing indicator values from the published CSV.

Most example values come from the recorded fixture, captured from version
2.0.2 of the data set on 28 September 2026. The rest cover edge cases the
fixture doesn't contain, such as padded values and unrecognised input.
"""

import pytest

from apprenticeship_explorer.parse import (
    Missing,
    UnrecognisedValueError,
    parse_indicator_value,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("7850", 7850), ("40", 40), ("0", 0), (" 3360 ", 3360)],
)
def test_whole_number_strings_become_integers(raw, expected):
    """Counts are parsed as integers, with surrounding spaces ignored."""
    result = parse_indicator_value(raw)
    assert result == expected
    assert isinstance(result, int)


@pytest.mark.parametrize(("raw", "expected"), [("24.9", 24.9), ("0.9", 0.9)])
def test_decimal_strings_become_floats(raw, expected):
    """Percentages are parsed as floats."""
    result = parse_indicator_value(raw)
    assert result == expected
    assert isinstance(result, float)


@pytest.mark.parametrize(
    ("raw", "reason"),
    [
        ("c", "suppressed to protect confidentiality"),
        ("x", "not available"),
        ("z", "not applicable"),
        ("low", "below the publication threshold"),
    ],
)
def test_markers_become_missing_values_that_keep_their_reason(raw, reason):
    """Each published marker becomes a Missing value that records its reason."""
    assert parse_indicator_value(raw) == Missing(marker=raw, reason=reason)


@pytest.mark.parametrize("raw", ["", "n/a", "nan", "inf", "C"])
def test_unrecognised_values_raise_an_error(raw):
    """Anything that isn't a finite number or a known marker is rejected.

    ``nan`` and ``inf`` are included because ``float()`` would otherwise
    accept them, and ``C`` because markers are matched case-sensitively.
    """
    with pytest.raises(UnrecognisedValueError):
        parse_indicator_value(raw)