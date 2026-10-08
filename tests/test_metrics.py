"""Tests for the national trend metrics.

``tests/fixtures/national-totals.csv`` holds the real national grand total
rows of version 2.0.2, one per year from 2017/18 to 2025/26, recorded from
the API. The expected values below are copied from that file.
"""

import csv
from pathlib import Path

import pytest

from apprenticeship_explorer.metrics import MEASURES, national_trend
from apprenticeship_explorer.time_period import AcademicYear

FIXTURES = Path(__file__).parent / "fixtures"


def national_rows():
    """Return the recorded national grand total rows, in the order the API gave them."""
    with open(FIXTURES / "national-totals.csv", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def row_for(rows, time_period):
    """Return the row for one year, as written in the CSV, such as ``202021``."""
    return next(row for row in rows if row["time_period"] == time_period)


def test_trend_covers_the_eight_complete_years_in_order():
    """2017/18 to 2024/25 come back oldest first, and the partial 2025/26 is left out."""
    years = [figures.year for figures in national_trend(national_rows())]
    assert years == [AcademicYear(start) for start in range(2017, 2025)]


@pytest.mark.parametrize(
    ("start_year", "starts", "achievements", "participation"),
    [
        (2017, 375760, 276160, 814790),
        (2020, 321440, 156530, 712990),
        (2024, 353500, 198330, 761480),
    ],
)
def test_values_match_the_recorded_national_totals(
    start_year, starts, achievements, participation
):
    """Each year's figures are the published national totals, unchanged."""
    figures = {f.year: f.values for f in national_trend(national_rows())}
    assert figures[AcademicYear(start_year)] == {
        "start_count": starts,
        "achievement_count": achievements,
        "participation_count": participation,
    }


def test_broken_down_rows_are_not_added_in():
    """A row for one level sits beside the total but is never added to it."""
    rows = national_rows()
    level_row = {**row_for(rows, "202021"), "apprenticeship_level": "Advanced"}
    rows.append({**level_row, "start_count": "100000"})
    figures = {f.year: f.values for f in national_trend(rows)}
    assert figures[AcademicYear(2020)]["start_count"] == 321440


def test_regional_rows_are_ignored():
    """Only the national row is used, even when a region has a row for the same year."""
    rows = national_rows()
    regional_row = {**row_for(rows, "202021"), "geographic_level": "Regional"}
    rows.append({**regional_row, "start_count": "50000"})
    figures = {f.year: f.values for f in national_trend(rows)}
    assert figures[AcademicYear(2020)]["start_count"] == 321440


def test_measures_are_named_by_what_they_count():
    """Starts and achievements count events, so no measure is labelled as learners."""
    assert list(MEASURES.values()) == ["Starts", "Achievements", "Participation"]
    assert not any("learner" in label.lower() for label in MEASURES.values())