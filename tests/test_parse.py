"""Tests for parsing indicator values from the published CSV.

Most example values come from the recorded fixture, captured from version
2.0.2 of the data set on 28 September 2026. The rest cover edge cases the
fixture doesn't contain, such as padded values and unrecognised input.
"""

import pytest

from apprenticeship_explorer.parse import (
    Missing,
    UnrecognisedValueError,
    parse_indicator_columns,
    parse_indicator_value,
)

# The indicator columns listed in the data set's metadata.
INDICATOR_COLUMNS = [
    "start_count",
    "achievement_count",
    "participation_count",
    "starts_percent",
    "achievements_percent",
]

# A real row from the recorded fixture: East Midlands, under 19, levy funded.
FIXTURE_ROW = {
    "time_period": "202122",
    "time_identifier": "Academic year",
    "geographic_level": "Regional",
    "country_code": "E92000001",
    "country_name": "England",
    "region_code": "E12000004",
    "region_name": "East Midlands",
    "apprenticeship_level": "Total",
    "age_youth_adult": "Under 19",
    "age_group": "Under 19",
    "funding_type": "Supported by ASA levy funds",
    "provider_type": "Total",
    "start_count": "2830",
    "achievement_count": "1270",
    "participation_count": "z",
    "starts_percent": "9.0",
    "achievements_percent": "10.1",
}


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


def test_indicator_columns_are_parsed():
    """Counts, percentages and markers in the indicator columns are all converted."""
    result = parse_indicator_columns(FIXTURE_ROW, INDICATOR_COLUMNS)
    assert result["start_count"] == 2830
    assert result["achievement_count"] == 1270
    assert result["participation_count"] == Missing(marker="z", reason="not applicable")
    assert result["starts_percent"] == 9.0
    assert result["achievements_percent"] == 10.1


def test_other_columns_are_left_unchanged():
    """Columns outside the indicators keep their raw values.

    ``time_period`` is the clearest case. It looks like a number, but it is a
    period code and must stay a string until it is normalised.
    """
    result = parse_indicator_columns(FIXTURE_ROW, INDICATOR_COLUMNS)
    for column, raw in FIXTURE_ROW.items():
        if column not in INDICATOR_COLUMNS:
            assert result[column] == raw
    assert result["time_period"] == "202122"


def test_region_code_z_survives_parsing_unchanged():
    """The region code ``z`` is kept as a code, not turned into a Missing value.

    No row in the captured sample uses this region, but the metadata lists ``z``
    as its location code, so the row is built from a real one with the region
    swapped in.
    """
    row = {
        **FIXTURE_ROW,
        "region_code": "z",
        "region_name": "Outside of England and unknown",
    }
    result = parse_indicator_columns(row, INDICATOR_COLUMNS)
    assert result["region_code"] == "z"
    assert result["region_name"] == "Outside of England and unknown"


def test_original_row_is_not_modified():
    """Parsing returns a new dictionary and leaves the input row as it was."""
    original = dict(FIXTURE_ROW)
    parse_indicator_columns(FIXTURE_ROW, INDICATOR_COLUMNS)
    assert FIXTURE_ROW == original


def test_misspelt_indicator_column_raises_an_error():
    """A column name that isn't in the row is reported, not silently skipped."""
    with pytest.raises(KeyError):
        parse_indicator_columns(FIXTURE_ROW, ["start_count", "start_cnt"])