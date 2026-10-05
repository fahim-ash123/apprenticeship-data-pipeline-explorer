"""Tests for normalising academic year time periods.

The three valid forms of 2021/22 are the ones the API returned for version
2.0.2 of the data set: ``202122`` in the CSV, and ``2021/2022`` and
``2021/22`` in the metadata. The other values are edge cases the API has not
returned but a strict parser must still handle.
"""

import pytest

from apprenticeship_explorer.time_period import (
    AcademicYear,
    InvalidTimePeriodError,
    normalise_time_period,
)


@pytest.mark.parametrize("raw", ["202122", "2021/2022", "2021/22"])
def test_each_published_form_normalises_to_2021_22(raw):
    """Each form the API uses for 2021/22 becomes the same academic year."""
    assert normalise_time_period(raw) == AcademicYear(start_year=2021)


def test_all_three_forms_are_equal_to_each_other():
    """The CSV and metadata forms are interchangeable once normalised."""
    csv_form = normalise_time_period("202122")
    period_form = normalise_time_period("2021/2022")
    label_form = normalise_time_period("2021/22")
    assert csv_form == period_form == label_form


def test_normalised_year_displays_as_the_published_label():
    """The normalised year prints in the form the report shows to users."""
    assert str(normalise_time_period("202122")) == "2021/22"


def test_surrounding_whitespace_is_ignored():
    """Padding is stripped, as it is for indicator values."""
    assert normalise_time_period(" 202122 ") == AcademicYear(start_year=2021)


@pytest.mark.parametrize("raw", ["199900", "1999/2000", "1999/00"])
def test_year_crossing_a_century_normalises(raw):
    """A year ending in 00 follows a year ending in 99, so 1999/00 is valid."""
    year = normalise_time_period(raw)
    assert year == AcademicYear(start_year=1999)
    assert year.label == "1999/00"


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "2021",
        "21/22",
        "202123",
        "2021/2023",
        "2021/23",
        "2021-22",
        "2021/22/23",
        "abcdef",
        "\uff12\uff10\uff12\uff11/22",
    ],
)
def test_invalid_values_raise_an_error(raw):
    """Anything that is not one of the three forms, with consecutive years, is rejected.

    The last case is 2021/22 written in full-width digits. Python's ``int``
    accepts those, so the parser must check for ASCII digits explicitly.
    """
    with pytest.raises(InvalidTimePeriodError):
        normalise_time_period(raw)


def test_error_message_includes_the_raw_value():
    """The error names the bad value, so it can be traced back to the source."""
    with pytest.raises(InvalidTimePeriodError, match="202123"):
        normalise_time_period("202123")