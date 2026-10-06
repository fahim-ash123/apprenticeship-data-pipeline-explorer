"""Tests for limiting the analysis to complete academic years.

The years 2017/18 to 2025/26 match the data set's coverage, with 2025/26 as
its latest, partial year. The years before and after that range are
hypothetical, to check the rule does not depend on a fixed year.
"""

import random

from apprenticeship_explorer.time_period import AcademicYear
from apprenticeship_explorer.window import complete_periods


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