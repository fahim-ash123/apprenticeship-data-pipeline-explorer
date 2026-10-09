"""Tests for comparing regions by the make-up of their starts.

``tests/fixtures/regional-levels.csv`` holds the real regional rows of version
2.0.2 for each region's total starts and its starts by level, with every other
filter at ``Total``, recorded from the API.
"""

import csv
from pathlib import Path

import pytest

from apprenticeship_explorer.parse import Missing, parse_indicator_value
from apprenticeship_explorer.regions import regional_comparison
from apprenticeship_explorer.time_period import AcademicYear

FIXTURES = Path(__file__).parent / "fixtures"

PUBLISHED_HIGHER_2024_25 = {
    "North East": 34.1,
    "North West": 38.6,
    "Yorkshire and The Humber": 33.7,
    "East Midlands": 38.9,
    "West Midlands": 39.1,
    "East of England": 42.3,
    "London": 50.5,
    "South East": 40.7,
    "South West": 35.6,
}


def regional_rows():
    """Return the recorded regional rows."""
    with open(FIXTURES / "regional-levels.csv", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def comparison_for(rows, start_year):
    """Return the comparison for one academic year."""
    return {c.year: c for c in regional_comparison(rows)}[AcademicYear(start_year)]


def test_london_share_is_its_higher_starts_over_its_own_total():
    """20,410 of London's 40,380 starts in 2024/25 were at higher level."""
    london = next(r for r in comparison_for(regional_rows(), 2024).regions if r.name == "London")
    assert london.share == pytest.approx(100 * 20410 / 40380)


def test_every_region_is_within_0_1_of_its_published_percentage():
    """Each share is within 0.1 points of the published starts percentage.

    Published percentages are calculated on unrounded counts (footnote 8), so a
    share worked out from the rounded counts can differ slightly. The West
    Midlands comes to 39.15% from the rounded counts and is published as 39.1%.
    """
    regions = comparison_for(regional_rows(), 2024).regions
    shares = {r.name: r.share for r in regions}
    assert shares == pytest.approx(PUBLISHED_HIGHER_2024_25, abs=0.1)


def test_regions_are_ranked_by_share_highest_first():
    """London leads in 2024/25 and Yorkshire and The Humber is last."""
    names = [r.name for r in comparison_for(regional_rows(), 2024).regions]
    assert names == [
        "London",
        "East of England",
        "South East",
        "West Midlands",
        "East Midlands",
        "North West",
        "South West",
        "North East",
        "Yorkshire and The Humber",
    ]


def test_ranking_by_share_differs_from_ranking_by_raw_counts():
    """By raw count, the South East's 22,510 higher starts would put it above London's 20,410."""
    rows = regional_rows()
    by_share = [r.name for r in comparison_for(rows, 2024).regions]
    higher = [
        r for r in rows
        if r["time_period"] == "202425"
        and r["apprenticeship_level"] == "Higher Apprenticeship"
        and r["region_code"] != "z"
    ]
    by_count = [r["region_name"] for r in sorted(higher, key=lambda r: -int(r["start_count"]))]
    assert by_count[0] == "South East"
    assert by_share[0] == "London"


def test_outside_england_is_reported_separately():
    """At 52.2% its share is the highest, but it is not in England, so it is not ranked."""
    comparison = comparison_for(regional_rows(), 2024)
    assert comparison.outside.name == "Outside of England and unknown"
    assert round(comparison.outside.share, 1) == 52.2
    assert all(r.code != "z" for r in comparison.regions)
    assert len(comparison.regions) == 9


def test_comparison_covers_the_eight_complete_years():
    """Every year from 2017/18 to 2024/25 is compared, and the partial 2025/26 is left out."""
    years = [c.year for c in regional_comparison(regional_rows())]
    assert years == [AcademicYear(y) for y in range(2017, 2025)]


def set_count(rows, region, level, value):
    """Replace one 2024/25 regional count, such as a level's starts, with a marker."""
    row = next(
        r for r in rows
        if r["time_period"] == "202425"
        and r["region_name"] == region
        and r["apprenticeship_level"] == level
    )
    row["start_count"] = value


def test_suppressed_region_is_reported_as_suppressed_and_ranked_last():
    """A suppressed region keeps its marker and its reason, and is listed after every share."""
    rows = regional_rows()
    set_count(rows, "London", "Higher Apprenticeship", "c")
    regions = comparison_for(rows, 2024).regions
    assert regions[-1].name == "London"
    assert isinstance(regions[-1].share, Missing)
    assert regions[-1].share == parse_indicator_value("c")
    assert regions[0].name == "East of England"


def test_number_of_suppressed_cells_is_stated():
    """Two suppressed counts in the breakdown are reported as two suppressed cells."""
    rows = regional_rows()
    set_count(rows, "London", "Higher Apprenticeship", "c")
    set_count(rows, "North East", "Total", "x")
    assert comparison_for(rows, 2024).suppressed_cells == 2


def test_suppression_outside_england_is_counted_too():
    """The outside region is not ranked, but its suppressed cells still count."""
    rows = regional_rows()
    set_count(rows, "Outside of England and unknown", "Higher Apprenticeship", "low")
    comparison = comparison_for(rows, 2024)
    assert comparison.outside.share == parse_indicator_value("low")
    assert comparison.suppressed_cells == 1


def test_recorded_2024_25_breakdown_has_no_suppressed_cells():
    """None of the counts read for 2024/25 is suppressed in the recorded data."""
    assert comparison_for(regional_rows(), 2024).suppressed_cells == 0