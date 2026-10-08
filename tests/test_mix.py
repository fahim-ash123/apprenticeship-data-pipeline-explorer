"""Tests for the level and age mix of starts.

``tests/fixtures/national-breakdowns.csv`` holds the real national rows of
version 2.0.2 that break starts down by one filter at a time, with every
other filter set to ``Total``, recorded from the API.
"""

import csv
from pathlib import Path

import pytest

from apprenticeship_explorer.metrics import FILTERS, age_mix, level_mix
from apprenticeship_explorer.parse import Missing, parse_indicator_value
from apprenticeship_explorer.time_period import AcademicYear

FIXTURES = Path(__file__).parent / "fixtures"
LEVELS = ["Intermediate Apprenticeship", "Advanced Apprenticeship", "Higher Apprenticeship"]
AGE_GROUPS = ["Under 19", "19 to 24", "25 plus"]


def breakdown_rows():
    """Return the recorded national breakdown rows."""
    with open(FIXTURES / "national-breakdowns.csv", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def test_level_shares_for_2024_25_match_the_recorded_counts():
    """65,680, 147,090 and 140,730 of 353,500 starts are 18.6%, 41.6% and 39.8%."""
    shares = {m.year: m.shares for m in level_mix(breakdown_rows())}[AcademicYear(2024)]
    assert shares == pytest.approx(
        {
            "Intermediate Apprenticeship": 100 * 65680 / 353500,
            "Advanced Apprenticeship": 100 * 147090 / 353500,
            "Higher Apprenticeship": 100 * 140730 / 353500,
        }
    )


def test_level_shares_round_to_the_published_percentages():
    """Rounded to one decimal place, the shares equal the published starts percentages."""
    shares = {m.year: m.shares for m in level_mix(breakdown_rows())}[AcademicYear(2024)]
    assert [round(shares[level], 1) for level in LEVELS] == [18.6, 41.6, 39.8]


def test_age_shares_for_2024_25_match_the_recorded_counts():
    """74,990, 97,240 and 181,270 of 353,500 starts round to the published 21.2%, 27.5% and 51.3%.

    The 19 to 24 and 25 plus rows have ``age_youth_adult`` set to ``19 plus``,
    so a selection with every other filter at ``Total`` would find no row.
    """
    shares = {m.year: m.shares for m in age_mix(breakdown_rows())}[AcademicYear(2024)]
    assert [round(shares[group], 1) for group in AGE_GROUPS] == [21.2, 27.5, 51.3]


@pytest.mark.parametrize("mix", [level_mix, age_mix])
def test_mix_covers_the_eight_complete_years(mix):
    """Both mixes run from 2017/18 to 2024/25, leaving out the partial 2025/26."""
    assert [m.year for m in mix(breakdown_rows())] == [AcademicYear(y) for y in range(2017, 2025)]


def test_level_mix_has_each_level_and_no_total():
    """Each year has the three levels, plus an Unknown level in 2017/18 only.

    The Total row is the denominator, so it is never an option.
    """
    for m in level_mix(breakdown_rows()):
        extra = ["Unknown"] if m.year == AcademicYear(2017) else []
        assert sorted(m.shares) == sorted(LEVELS + extra)


def test_age_mix_has_each_age_group_and_no_total():
    """Each year has the three age groups, and the Total row is never an option."""
    assert all(sorted(m.shares) == sorted(AGE_GROUPS) for m in age_mix(breakdown_rows()))


def test_unknown_level_in_2017_18_is_carried_as_low():
    """The recorded 2017/18 Unknown level has ``low`` in its count, so its share is missing."""
    shares = {m.year: m.shares for m in level_mix(breakdown_rows())}[AcademicYear(2017)]
    assert shares["Unknown"] == parse_indicator_value("low")


@pytest.mark.parametrize("mix", [level_mix, age_mix])
def test_shares_sum_to_100_within_rounding_tolerance(mix):
    """Counts are rounded to the nearest 10, so each year's shares sum to 100 within 0.5.

    A missing share, such as the 2017/18 Unknown level, is left out of the sum.
    """
    for m in mix(breakdown_rows()):
        known = [share for share in m.shares.values() if not isinstance(share, Missing)]
        assert sum(known) == pytest.approx(100, abs=0.5)


def row_for(rows, time_period, **filters):
    """Return the national row for one year with the given filter values, others at Total."""
    wanted = {**{f: "Total" for f in FILTERS}, **filters}
    return next(
        r for r in rows
        if r["time_period"] == time_period and all(r[f] == v for f, v in wanted.items())
    )


@pytest.mark.parametrize("marker", ["c", "x", "z", "low"])
def test_suppressed_count_gives_a_missing_share(marker):
    """A suppressed count becomes a missing share with its reason, never zero."""
    rows = breakdown_rows()
    row_for(rows, "202425", apprenticeship_level="Higher Apprenticeship")["start_count"] = marker
    shares = {m.year: m.shares for m in level_mix(rows)}[AcademicYear(2024)]
    assert isinstance(shares["Higher Apprenticeship"], Missing)
    assert shares["Higher Apprenticeship"] == parse_indicator_value(marker)


def test_suppressed_total_makes_every_share_missing():
    """Without a total there is no denominator, so no share can be given."""
    rows = breakdown_rows()
    row_for(rows, "202425")["start_count"] = "c"
    shares = {m.year: m.shares for m in level_mix(rows)}[AcademicYear(2024)]
    assert all(share == parse_indicator_value("c") for share in shares.values())