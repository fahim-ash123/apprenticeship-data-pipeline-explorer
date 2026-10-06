"""Tests for selecting single cells without double counting.

The sample has the same structure as the published file, with ``Total`` rows
for each filter alongside the rows they sum. The labels and counts are
invented, and the counts are chosen so the subtotals add up exactly.
"""

import pytest

from apprenticeship_explorer.parse import parse_indicator_value
from apprenticeship_explorer.selector import (
    AmbiguousSelectionError,
    NoMatchingRowError,
    select_cell,
)

DIMENSIONS = ("time_period", "geographic_level", "apprenticeship_level", "age_group")

STARTS = {
    "Intermediate": {"Under 19": 10, "19-24": 20, "25+": 30},
    "Advanced": {"Under 19": 40, "19-24": 50, "25+": 60},
    "Higher": {"Under 19": 5, "19-24": 15, "25+": 25},
}


def sample_rows():
    """Return one year of national rows, with every subtotal the file would include.

    Returns:
        Sixteen rows: each level by each age group, a ``Total`` age group for
        each level, a ``Total`` level for each age group, and the grand total.
    """
    ages = ["Under 19", "19-24", "25+"]
    grid = {level: dict(by_age) for level, by_age in STARTS.items()}
    for by_age in grid.values():
        by_age["Total"] = sum(by_age[age] for age in ages)
    grid["Total"] = {age: sum(grid[level][age] for level in STARTS) for age in ages + ["Total"]}
    return [
        {
            "time_period": "202122",
            "geographic_level": "National",
            "apprenticeship_level": level,
            "age_group": age,
            "start_count": str(count),
        }
        for level, by_age in grid.items()
        for age, count in by_age.items()
    ]


def selection(level="Total", age="Total"):
    """Return a complete selection for 2021/22 at national level."""
    return {
        "time_period": "202122",
        "geographic_level": "National",
        "apprenticeship_level": level,
        "age_group": age,
    }


def test_selects_the_one_row_for_a_broken_down_cell():
    """Advanced apprenticeships for 19 to 24 year olds come from one row."""
    row = select_cell(sample_rows(), DIMENSIONS, selection("Advanced", "19-24"))
    assert row["start_count"] == "50"


def test_selects_the_grand_total_row():
    """With ``Total`` for both filters, the grand total row is returned."""
    row = select_cell(sample_rows(), DIMENSIONS, selection())
    assert row["start_count"] == "255"


def test_selects_a_subtotal_row():
    """``Total`` for one filter returns that filter's subtotal row only."""
    row = select_cell(sample_rows(), DIMENSIONS, selection("Higher", "Total"))
    assert row["start_count"] == "45"


def test_no_matching_row_raises():
    """A selection that matches nothing is an error, not an empty result."""
    with pytest.raises(NoMatchingRowError):
        select_cell(sample_rows(), DIMENSIONS, selection("Degree", "Total"))


def test_more_than_one_matching_row_raises():
    """A repeated row would make the figure ambiguous, so it is rejected."""
    rows = sample_rows()
    rows.append(dict(rows[0]))
    with pytest.raises(AmbiguousSelectionError):
        select_cell(rows, DIMENSIONS, selection("Intermediate", "Under 19"))


def test_summing_rows_naively_inflates_the_total():
    """Adding up every row for the year counts each start four times over.

    Each broken-down count appears once in its own row, once in its level's
    subtotal, once in its age group's subtotal and once in the grand total.
    """
    naive = sum(parse_indicator_value(row["start_count"]) for row in sample_rows())
    grand_total = select_cell(sample_rows(), DIMENSIONS, selection())
    correct = parse_indicator_value(grand_total["start_count"])
    assert naive != correct
    assert naive == 4 * correct