"""Tests for the metadata model with namespaced identifiers.

The sample follows the shape of the ``/meta`` response. The colliding
identifiers ``mU59K`` and ``jI4AM``, and the columns and option they belong
to, are real values from version 2.0.2 of the data set. The other identifiers,
labels and codes are invented to keep the sample small.
"""

import pytest

from apprenticeship_explorer.metadata import (
    DataSetMetadata,
    MetadataError,
    UnknownIdentifierError,
    )
from apprenticeship_explorer.time_period import AcademicYear

PROVIDER_TYPE = "Pv7tY"


def sample_meta():
    """Return a fresh copy of the sample metadata, so tests can change it safely."""
    return {
        "filters": [
            {
                "id": "mU59K",
                "column": "age_group",
                "label": "Age group",
                "options": [
                    {"id": "Ab1cD", "label": "Under 19"},
                    {"id": "Ef2gH", "label": "Total"},
                ],
            },
            {
                "id": "jI4AM",
                "column": "age_youth_adult",
                "label": "Age, youth or adult",
                "options": [{"id": "Ij3kL", "label": "Total"}],
            },
            {
                "id": PROVIDER_TYPE,
                "column": "provider_type",
                "label": "Provider type",
                "options": [
                    {"id": "jI4AM", "label": "Schools"},
                    {"id": "Mn4oP", "label": "Total"},
                ],
            },
        ],
        "indicators": [
            {
                "id": "mU59K",
                "column": "achievement_count",
                "label": "Achievements",
                "unit": "",
                "decimalPlaces": 0,
            },
            {
                "id": "Qr5sT",
                "column": "starts_percent",
                "label": "Starts, percentage",
                "unit": "%",
                "decimalPlaces": 1,
            },
        ],
        "locations": [
            {
                "level": {"code": "NAT", "label": "National"},
                "options": [{"id": "Uv6wX", "label": "England", "code": "E92000001"}],
            },
            {
                "level": {"code": "REG", "label": "Regional"},
                "options": [
                    {"id": "Yz7aB", "label": "North East", "code": "E12000001"},
                    {"id": "Cd8eF", "label": "Outside of England and unknown", "code": "z"},
                ],
            },
        ],
        "timePeriods": [
            {"code": "AY", "period": "2024/2025", "label": "2024/25"},
            {"code": "AY", "period": "2017/2018", "label": "2017/18"},
        ],
    }


def test_each_type_is_held_in_its_own_collection():
    """Filters, indicators, options, locations and time periods are kept apart."""
    meta = DataSetMetadata.from_api(sample_meta())
    assert set(meta.filters) == {"mU59K", "jI4AM", PROVIDER_TYPE}
    assert set(meta.indicators) == {"mU59K", "Qr5sT"}
    assert set(meta.filters[PROVIDER_TYPE].options) == {"jI4AM", "Mn4oP"}
    assert set(meta.locations) == {"NAT", "REG"}
    assert len(meta.time_periods) == 2


def test_mu59k_resolves_to_the_age_group_filter():
    """In the filter namespace, ``mU59K`` is the ``age_group`` filter."""
    meta = DataSetMetadata.from_api(sample_meta())
    assert meta.filter("mU59K").column == "age_group"


def test_mu59k_resolves_to_the_achievement_count_indicator():
    """In the indicator namespace, the same ``mU59K`` is ``achievement_count``."""
    meta = DataSetMetadata.from_api(sample_meta())
    assert meta.indicator("mU59K").column == "achievement_count"


def test_ji4am_resolves_to_the_age_youth_adult_filter():
    """In the filter namespace, ``jI4AM`` is the ``age_youth_adult`` filter."""
    meta = DataSetMetadata.from_api(sample_meta())
    assert meta.filter("jI4AM").column == "age_youth_adult"


def test_ji4am_resolves_to_the_schools_option_of_provider_type():
    """Among provider type's options, the same ``jI4AM`` is "Schools"."""
    meta = DataSetMetadata.from_api(sample_meta())
    assert meta.filter_option(PROVIDER_TYPE, "jI4AM").label == "Schools"


def test_indicator_keeps_its_unit_and_decimal_places():
    """Units and decimal places are kept, because percentages need them."""
    indicator = DataSetMetadata.from_api(sample_meta()).indicator("Qr5sT")
    assert (indicator.unit, indicator.decimal_places) == ("%", 1)


def test_location_is_found_within_its_level():
    """A location is looked up by its level code and its identifier together."""
    meta = DataSetMetadata.from_api(sample_meta())
    assert meta.location("REG", "Yz7aB").label == "North East"


def test_location_code_z_is_kept_as_text():
    """The code ``z`` for "Outside of England and unknown" is a code, not a marker."""
    meta = DataSetMetadata.from_api(sample_meta())
    assert meta.location("REG", "Cd8eF").code == "z"


def test_time_periods_are_normalised_and_in_chronological_order():
    """Time periods become academic years, sorted whatever order the API used."""
    meta = DataSetMetadata.from_api(sample_meta())
    assert meta.time_periods == (AcademicYear(2017), AcademicYear(2024))

def test_indicator_identifier_is_not_found_among_filters():
    """An identifier that exists only as an indicator is not a filter."""
    meta = DataSetMetadata.from_api(sample_meta())
    with pytest.raises(UnknownIdentifierError, match="filter.*Qr5sT"):
        meta.filter("Qr5sT")


def test_filter_identifier_is_not_found_among_indicators():
    """``jI4AM`` is a filter and an option, but never an indicator."""
    meta = DataSetMetadata.from_api(sample_meta())
    with pytest.raises(UnknownIdentifierError, match="indicator.*jI4AM"):
        meta.indicator("jI4AM")


def test_option_is_found_only_within_its_own_filter():
    """The "Schools" option belongs to provider type, so ``age_group`` lacks it."""
    meta = DataSetMetadata.from_api(sample_meta())
    with pytest.raises(UnknownIdentifierError, match="mU59K.*jI4AM"):
        meta.filter_option("mU59K", "jI4AM")


def test_option_lookup_in_an_unknown_filter_raises():
    """Asking for an option of a filter that does not exist is an error."""
    meta = DataSetMetadata.from_api(sample_meta())
    with pytest.raises(UnknownIdentifierError, match="filter.*Zz9zZ"):
        meta.filter_option("Zz9zZ", "jI4AM")


def test_location_is_not_found_at_another_level():
    """A regional location cannot be found by searching the national level."""
    meta = DataSetMetadata.from_api(sample_meta())
    with pytest.raises(UnknownIdentifierError, match="NAT.*Yz7aB"):
        meta.location("NAT", "Yz7aB")


def test_unknown_level_raises():
    """A level the data set does not have is an error, not an empty result."""
    meta = DataSetMetadata.from_api(sample_meta())
    with pytest.raises(UnknownIdentifierError, match="LA"):
        meta.location("LA", "Yz7aB")


def test_repeated_filter_identifier_raises():
    """A repeat within one namespace would hide a filter, so it is rejected."""
    meta = sample_meta()
    meta["filters"].append(dict(meta["filters"][0], column="age_group_copy"))
    with pytest.raises(MetadataError, match="mU59K"):
        DataSetMetadata.from_api(meta)


def test_repeated_option_identifier_within_a_filter_raises():
    """Two options of one filter cannot share an identifier."""
    meta = sample_meta()
    meta["filters"][2]["options"].append({"id": "jI4AM", "label": "Schools again"})
    with pytest.raises(MetadataError, match="jI4AM"):
        DataSetMetadata.from_api(meta)


def test_time_period_whose_period_and_label_disagree_raises():
    """The ``period`` and ``label`` fields must describe the same academic year."""
    meta = sample_meta()
    meta["timePeriods"][0]["label"] = "2023/24"
    with pytest.raises(MetadataError, match="2024/2025"):
        DataSetMetadata.from_api(meta)


def test_time_period_that_is_not_an_academic_year_raises():
    """Only academic years, code ``AY``, are supported by this data set."""
    meta = sample_meta()
    meta["timePeriods"][0]["code"] = "CY"
    with pytest.raises(MetadataError, match="CY"):
        DataSetMetadata.from_api(meta)