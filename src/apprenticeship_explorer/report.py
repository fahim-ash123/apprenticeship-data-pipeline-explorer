"""Assemble the report's sections from the tested package functions.

The notebook calls these functions and displays what they return, so it holds
no analytical logic of its own. Each section follows prototype version 2, and
every chart comes with a caveat line, a written summary and a table, which
together are its text alternative.
"""

from dataclasses import dataclass
from datetime import date

from apprenticeship_explorer.client import ApiClient

DATA_SET_ID = "1d419801-a90e-f970-9335-a13623faccbe"
VERSION = "2.0.2"


class Markdown(str):
    """Text the notebook displays as Markdown."""

    def _repr_markdown_(self) -> str:
        """Return the text for the notebook to render."""
        return str(self)


class Html(str):
    """Text the notebook displays as HTML."""

    def _repr_html_(self) -> str:
        """Return the text for the notebook to render."""
        return str(self)


@dataclass(frozen=True)
class ReportData:
    """Everything the report needs, retrieved once.

    Attributes:
        rows: The data rows of the pinned version, every value as text.
        version: The pinned data set version.
        retrieved: The date the data was retrieved.
        versions: Every published version, as the API returned them.
        schemas: Each version's metadata, keyed by version.
    """

    rows: list
    version: str
    retrieved: date
    versions: list
    schemas: dict


def load(client: ApiClient | None = None, version: str = VERSION, today=None) -> ReportData:
    """Retrieve the pinned version of the data, its version list and every schema.

    Args:
        client: The API client. A real client is made if none is given.
        version: The data set version to pin.
        today: The retrieval date. Defaults to today.

    Returns:
        The data the report is built from.
    """
    # Deliberately not implemented yet. The tests are written first.
    raise NotImplementedError


def header(data: ReportData) -> Markdown:
    """Return the title, data set version, retrieval date and analysis window.

    Args:
        data: The report data.

    Returns:
        The header as Markdown.
    """
    raise NotImplementedError


def key_findings(data: ReportData) -> Markdown:
    """Return the four headline findings in plain language.

    Args:
        data: The report data.

    Returns:
        The findings as a Markdown list.
    """
    raise NotImplementedError


def over_time(data: ReportData) -> Html:
    """Return the trend in starts and achievements, and the mix of levels.

    Args:
        data: The report data.

    Returns:
        The section as HTML.
    """
    raise NotImplementedError


def age_groups(data: ReportData) -> Html:
    """Return each age group's share of starts over time.

    Args:
        data: The report data.

    Returns:
        The section as HTML.
    """
    raise NotImplementedError


def funding(data: ReportData) -> Html:
    """Return levy-funded and other starts as shares, from 2020/21.

    Args:
        data: The report data.

    Returns:
        The section as HTML.
    """
    raise NotImplementedError