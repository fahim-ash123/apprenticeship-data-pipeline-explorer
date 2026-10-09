"""Tests for the data quality profile.

The rows are built in each test, so every expected count is known exactly.
They have the same columns as the published file, and the real profile of the
full file is produced by the notebook.
"""

from collections import Counter

import pytest

from apprenticeship_explorer.quality import (
    LEVY,
    breakdown,
    participation_z_in_all_levy_rows,
    profile,
    suppression_by_granularity,
)


def row(level="Total", age="Total", youth="Total", funding="Total", provider="Total", **values):
    """Return one data row with the given filters and indicator values.

    Indicators not given are ordinary numbers, so they hold no marker.
    """
    return {
        "apprenticeship_level": level,
        "age_group": age,
        "age_youth_adult": youth,
        "funding_type": funding,
        "provider_type": provider,
        "start_count": "100",
        "achievement_count": "50",
        "participation_count": "200",
        "starts_percent": "100.0",
        "achievements_percent": "100.0",
        **values,
    }


def sample_rows():
    """Return five rows with one marker each, in different indicators and breakdowns."""
    return [
        row(start_count="c"),
        row(level="Higher Apprenticeship", achievement_count="x"),
        row(level="Higher Apprenticeship", funding="Other", participation_count="z"),
        row(age="19 to 24", youth="19 plus", starts_percent="low"),
        row(level="Higher Apprenticeship", participation_count="low"),
    ]


def test_rows_loaded_counts_every_row():
    """Every row read is counted, including rows with no marker."""
    assert profile([*sample_rows(), row()]).rows_loaded == 6


def test_markers_are_counted_by_indicator():
    """Each marker is counted under the column it appears in."""
    by_indicator = profile(sample_rows()).markers_by_indicator
    assert by_indicator["start_count"] == Counter({"c": 1})
    assert by_indicator["achievement_count"] == Counter({"x": 1})
    assert by_indicator["participation_count"] == Counter({"z": 1, "low": 1})
    assert by_indicator["starts_percent"] == Counter({"low": 1})
    assert by_indicator["achievements_percent"] == Counter()


def test_markers_are_counted_by_breakdown():
    """Each marker is counted under the filters its row is broken down by."""
    assert profile(sample_rows()).markers_by_breakdown == {
        "Total": Counter({"c": 1}),
        "apprenticeship_level": Counter({"x": 1, "low": 1}),
        "apprenticeship_level+funding_type": Counter({"z": 1}),
        "age_group": Counter({"low": 1}),
    }


def test_low_is_counted_in_count_columns_only():
    """``low`` in a percentage is defined by footnote 8, so only its use in a count is reported."""
    assert profile(sample_rows()).low_in_count_columns == 1


def test_suppressed_cells_are_totalled_by_marker():
    """Across all indicators there is one ``c``, one ``x``, one ``z`` and two ``low``."""
    assert profile(sample_rows()).suppressed_cells_by_marker == Counter(
        {"c": 1, "x": 1, "z": 1, "low": 2}
    )


def test_subtotal_rows_are_rows_with_any_filter_at_total():
    """Only a row broken down by every filter is not a subtotal."""
    full = row("Higher Apprenticeship", "19 to 24", "19 plus", "Other", "Schools")
    assert profile([row(), row(level="Advanced Apprenticeship"), full]).subtotal_rows == 2


def test_numbers_including_zero_are_not_markers():
    """A real zero is a value, so it is never counted as a marker."""
    assert profile([row(start_count="0")]).suppressed_cells_by_marker == Counter()


def test_age_group_breakdown_does_not_count_the_youth_split_twice():
    """An age group row carries its youth or adult value, but it is one breakdown."""
    assert breakdown(row(age="25 plus", youth="19 plus")) == "age_group"
    assert breakdown(row(youth="Under 19")) == "age_youth_adult"

def test_suppression_rises_with_granularity():
    """No total cell is suppressed, one cell in ten at one filter, and every cell at two."""
    rows = [
        row(),
        row(level="Higher Apprenticeship", start_count="c"),
        row(level="Advanced Apprenticeship"),
        row(
            level="Higher Apprenticeship",
            funding=LEVY,
            start_count="c",
            achievement_count="c",
            participation_count="c",
            starts_percent="c",
            achievements_percent="c",
        ),
    ]
    assert suppression_by_granularity(rows) == {0: 0.0, 1: 10.0, 2: 100.0}


def test_only_c_counts_as_suppressed():
    """``x``, ``z`` and ``low`` mean unavailable, not applicable and small, not suppressed."""
    rows = [row(start_count="x", achievement_count="z", starts_percent="low")]
    assert suppression_by_granularity(rows) == {0: 0.0}


def test_age_group_rows_count_as_one_filter():
    """An age group row is broken down once, even though it also carries a youth value."""
    assert suppression_by_granularity([row(age="Under 19", youth="Under 19")]) == {1: 0.0}


def test_participation_is_z_in_every_levy_row():
    """When every levy-funded row has ``z`` for participation, the check confirms it."""
    rows = [row(funding=LEVY, participation_count="z"), row(participation_count="200")]
    assert participation_z_in_all_levy_rows(rows) is True


def test_one_levy_row_with_a_participation_value_fails_the_check():
    """A single levy-funded row with a real participation count means the rule does not hold."""
    rows = [row(funding=LEVY, participation_count="z"), row(funding=LEVY, participation_count="9")]
    assert participation_z_in_all_levy_rows(rows) is False


def test_no_levy_rows_cannot_be_confirmed():
    """With nothing to check, the function refuses to answer instead of saying yes."""
    with pytest.raises(ValueError, match="levy"):
        participation_z_in_all_levy_rows([row()])