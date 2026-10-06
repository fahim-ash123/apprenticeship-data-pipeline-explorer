"""Tests for limiting the analysis to complete academic years.

The years 2017/18 to 2025/26 match the data set's coverage, with 2025/26 as
its latest, partial year. The years before and after that range are
hypothetical, to check the rule does not depend on a fixed year.
"""

import random

import pytest

from apprenticeship_explorer.time_period import AcademicYear, normalise_time_period
from apprenticeship_explorer.window import (
    EmptyWindowError,
    complete_periods,
    filter_to_window,
)


def years(first, last):
    """Return the academic years starting in ``first`` to ``last`` inclusive."""
    return [AcademicYear(year) for year in range(first, last + 1)]


def test_latest_period_is_left_out():
    """The latest year, 2025/26, is partial and is not in the window."""
    assert AcademicYear(2025) not in complete_periods(years(2017, 2025))


def test_default_window_is_the_eight_full_years():
    """By default the window runs from 2017/18 to 2024/25."""
    assert complete_periods(years(2017, 2025)) == tuple(years(2017, 2024))


def test_default_start_drops_earlier_years():
    """Years before 2017/18 are left out when the data goes back further."""
    assert complete_periods(years(2014, 2025))[0] == AcademicYear(2017)


def test_start_can_be_changed():
    """The start is a parameter, as the levy comparison begins in 2020/21."""
    window = complete_periods(years(2017, 2025), start=AcademicYear(2020))
    assert window == tuple(years(2020, 2024))


def test_rule_moves_on_when_a_later_year_is_added():
    """With 2026/27 published, 2026/27 is left out and 2025/26 is kept."""
    window = complete_periods(years(2017, 2026))
    assert AcademicYear(2026) not in window
    assert window[-1] == AcademicYear(2025)


def test_order_and_repeats_in_the_input_do_not_matter():
    """Periods arrive once per row in no set order, so both are handled."""
    shuffled = years(2017, 2025) * 3
    random.Random(1).shuffle(shuffled)
    assert complete_periods(shuffled) == tuple(years(2017, 2024))


def csv_rows(first, last):
    """Return two rows per year, with time periods in the CSV form, such as ``202526``.

    Args:
        first: The start year of the first academic year.
        last: The start year of the last academic year.

    Returns:
        Rows for each year, with ``Total`` and ``Under 19`` age groups.
    """
    return [
        {"time_period": f"{year}{(year + 1) % 100:02d}", "age_group": age}
        for year in range(first, last + 1)
        for age in ("Total", "Under 19")
    ]


def test_2025_26_never_appears_in_the_filtered_rows():
    """No row from the partial year 2025/26 survives the filter."""
    kept = filter_to_window(csv_rows(2017, 2025))
    assert all(normalise_time_period(row["time_period"]) != AcademicYear(2025) for row in kept)


def test_rows_inside_the_window_are_kept_unchanged_and_in_order():
    """The filter removes rows but never alters or reorders the ones it keeps."""
    rows = csv_rows(2017, 2025)
    assert filter_to_window(rows) == rows[:-2]


def test_filter_leaves_out_the_latest_year_in_the_rows():
    """With 2026/27 rows present, 2025/26 rows are kept and 2026/27 rows are not."""
    kept = {row["time_period"] for row in filter_to_window(csv_rows(2017, 2026))}
    assert "202526" in kept
    assert "202627" not in kept


def test_filter_uses_the_start_parameter():
    """Rows before the chosen start are removed."""
    kept = filter_to_window(csv_rows(2017, 2025), start=AcademicYear(2020))
    assert min(row["time_period"] for row in kept) == "202021"


def test_start_at_the_latest_year_leaves_an_empty_window():
    """Starting at the partial year leaves nothing to analyse, which is an error."""
    with pytest.raises(EmptyWindowError):
        complete_periods(years(2017, 2025), start=AcademicYear(2025))


def test_no_periods_at_all_raises():
    """An empty input is reported as an empty window, not as a crash."""
    with pytest.raises(EmptyWindowError):
        complete_periods([])
    