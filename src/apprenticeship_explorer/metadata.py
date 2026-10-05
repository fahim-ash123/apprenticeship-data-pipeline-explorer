"""Model the metadata of an Explore Education Statistics data set.

Identifiers in the metadata are unique only within their own type. In version
2.0.2 of the apprenticeships data set, ``mU59K`` is both the ``age_group``
filter and the ``achievement_count`` indicator, and ``jI4AM`` is both the
``age_youth_adult`` filter and the "Schools" option of ``provider_type``. One
lookup table keyed by identifier would return the wrong thing, so each type is
held in its own namespace and every lookup names the namespace it searches.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from apprenticeship_explorer.time_period import AcademicYear, normalise_time_period


class MetadataError(ValueError):
    """Raised when the metadata breaks a rule the model relies on."""


class UnknownIdentifierError(LookupError):
    """Raised when an identifier does not exist in the namespace searched."""


@dataclass(frozen=True)
class FilterOption:
    """One option of a filter, such as "Schools" for ``provider_type``.

    Attributes:
        id: The option's identifier, unique only within its filter.
        label: The option's label as published.
    """

    id: str
    label: str


@dataclass(frozen=True)
class Filter:
    """A filter and its options.

    Attributes:
        id: The filter's identifier, unique only among filters.
        column: The filter's column name in the CSV, such as ``age_group``.
        label: The filter's label as published.
        options: The filter's options, keyed by option identifier.
    """

    id: str
    column: str
    label: str
    options: Mapping[str, FilterOption]


@dataclass(frozen=True)
class Indicator:
    """An indicator, such as ``start_count``.

    Attributes:
        id: The indicator's identifier, unique only among indicators.
        column: The indicator's column name in the CSV.
        label: The indicator's label as published.
        unit: The unit, such as ``%``, or an empty string for counts.
        decimal_places: The published number of decimal places, if given.
    """

    id: str
    column: str
    label: str
    unit: str
    decimal_places: int | None


@dataclass(frozen=True)
class Location:
    """A location at one geographic level.

    Attributes:
        id: The location's identifier, unique only within its level.
        label: The location's name as published.
        code: The location's code, if it has one. This is text, because codes
            such as ``z`` are not numbers.
    """

    id: str
    label: str
    code: str | None


@dataclass(frozen=True)
class DataSetMetadata:
    """The metadata of one data set version, with one namespace per type.

    Attributes:
        filters: Filters keyed by filter identifier.
        indicators: Indicators keyed by indicator identifier.
        locations: Locations keyed by level code, then by location identifier.
        time_periods: The data set's academic years in chronological order.
    """

    filters: Mapping[str, Filter]
    indicators: Mapping[str, Indicator]
    locations: Mapping[str, Mapping[str, Location]]
    time_periods: tuple[AcademicYear, ...]

    @classmethod
    def from_api(cls, meta: Mapping[str, Any]) -> "DataSetMetadata":
        """Build the model from the JSON returned by the ``/meta`` endpoint.

        Args:
            meta: The decoded JSON response.

        Returns:
            The metadata, split into its namespaces.

        Raises:
            MetadataError: If an identifier repeats within one namespace, or a
                time period is not a consistent academic year.
        """
        filters = {
            f["id"]: Filter(
                id=f["id"],
                column=f["column"],
                label=f["label"],
                options={o["id"]: FilterOption(o["id"], o["label"]) for o in f["options"]},
            )
            for f in meta["filters"]
        }
        indicators = {
            i["id"]: Indicator(
                id=i["id"],
                column=i["column"],
                label=i["label"],
                unit=i.get("unit", ""),
                decimal_places=i.get("decimalPlaces"),
            )
            for i in meta["indicators"]
        }
        locations = {
            group["level"]["code"]: {
                o["id"]: Location(o["id"], o["label"], o.get("code"))
                for o in group["options"]
            }
            for group in meta["locations"]
        }
        time_periods = tuple(
            sorted(normalise_time_period(t["period"]) for t in meta["timePeriods"])
        )
        return cls(filters, indicators, locations, time_periods)

    def filter(self, filter_id: str) -> Filter:
        """Look up a filter by its identifier.

        Args:
            filter_id: The filter's identifier.

        Returns:
            The filter, with its options.

        Raises:
            UnknownIdentifierError: If no filter has that identifier.
        """
        return self.filters[filter_id]

    def indicator(self, indicator_id: str) -> Indicator:
        """Look up an indicator by its identifier.

        Args:
            indicator_id: The indicator's identifier.

        Returns:
            The indicator.

        Raises:
            UnknownIdentifierError: If no indicator has that identifier.
        """
        return self.indicators[indicator_id]

    def filter_option(self, filter_id: str, option_id: str) -> FilterOption:
        """Look up an option within the filter it belongs to.

        Args:
            filter_id: The identifier of the filter the option belongs to.
            option_id: The option's identifier.

        Returns:
            The option.

        Raises:
            UnknownIdentifierError: If the filter does not exist, or has no
                option with that identifier.
        """
        return self.filters[filter_id].options[option_id]

    def location(self, level: str, location_id: str) -> Location:
        """Look up a location within its geographic level, such as ``REG``.

        Args:
            level: The geographic level code.
            location_id: The location's identifier.

        Returns:
            The location.

        Raises:
            UnknownIdentifierError: If the level does not exist, or has no
                location with that identifier.
        """
        return self.locations[level][location_id]