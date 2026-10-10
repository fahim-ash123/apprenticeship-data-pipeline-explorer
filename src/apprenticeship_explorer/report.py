"""Assemble the report's sections from the tested package functions.

The notebook calls these functions and displays what they return, so it holds
no analytical logic of its own. Each section follows prototype version 2, and
every chart comes with a caveat line, a written summary and a table, which
together are its text alternative.
"""

import base64
import csv
import html
import io
from dataclasses import dataclass
from datetime import date

from apprenticeship_explorer import __version__
from apprenticeship_explorer.charts import Chart, bar_chart, line_chart
from apprenticeship_explorer.client import ApiClient
from apprenticeship_explorer.metrics import age_mix, funding_mix, level_mix, national_trend
from apprenticeship_explorer.parse import Missing
from apprenticeship_explorer.quality import (
    participation_z_in_all_levy_rows,
    profile,
    suppression_by_granularity,
)
from apprenticeship_explorer.regions import regional_comparison
from apprenticeship_explorer.time_period import normalise_time_period
from apprenticeship_explorer.versions import compare_schemas, sort_versions

DATA_SET_ID = "1d419801-a90e-f970-9335-a13623faccbe"
VERSION = "2.0.2"
REPOSITORY = "https://github.com/fahim-ash123/apprenticeship-data-pipeline-explorer"
LEVY = "Supported by ASA levy funds"
SECTIONS = (
    "header",
    "key_findings",
    "over_time",
    "age_groups",
    "funding",
    "regions",
    "about_the_data",
    "technical_notes",
)

NOT_A_RATE = (
    "This is not an achievement rate. Starts and achievements count different "
    "apprenticeships, and an apprenticeship achieved this year may have started in an "
    "earlier one, so dividing achievements by starts does not give a rate "
    "(footnotes 10 and 11)."
)

KNOWN_TRAPS = (
    "Identifiers are unique only within their own type: mU59K is both the age_group "
    "filter and the achievement_count indicator.",
    "The letter z is a suppression marker in value columns and the location code for "
    "Outside of England and unknown.",
    "One academic year is written three ways: 202122, 2021/2022 and 2021/22.",
    "Versions are returned out of order, with two-part and three-part numbers.",
    "Patch release 1.0.1 added a filter, so a patch can change the structure.",
    "The file contains pre-computed subtotals, so adding up rows double counts.",
    "low appears in count columns, although footnote 8 defines it only for percentages.",
    "Age group rows carry their youth or adult value instead of Total.",
)


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
    client = client or ApiClient()
    rows = list(csv.DictReader(io.StringIO(client.csv(DATA_SET_ID, version))))
    versions = [entry["version"] for entry in client.versions(DATA_SET_ID)]
    schemas = {v: client.metadata(DATA_SET_ID, v) for v in versions}
    return ReportData(rows, version, today or date.today(), versions, schemas)


def header(data: ReportData) -> Markdown:
    """Return the title, data set version, retrieval date and analysis window.

    Args:
        data: The report data.

    Returns:
        The header as Markdown.
    """
    first, last, latest = _window(data)
    return Markdown(
        "# Apprenticeship starts and achievements in England\n\n"
        "Headline full-year figures from Explore Education Statistics.\n\n"
        f"Data set version {data.version}, retrieved {_day(data.retrieved)}. "
        f"The analysis covers {first} to {last}. It starts in {first}, the first year of "
        f"the data, and leaves out {latest}, the latest year, because it is provisional "
        "and covers August to April only (footnote 12)."
    )


def key_findings(data: ReportData) -> Markdown:
    """Return the four headline findings in plain language.

    Args:
        data: The report data.

    Returns:
        The findings as a Markdown list.
    """
    trend = national_trend(data.rows)
    first, last = trend[0], trend[-1]
    change = 100 * (last.values["start_count"] / first.values["start_count"] - 1)
    direction = "fell" if change < 0 else "rose"
    levels = level_mix(data.rows)
    higher = "Higher Apprenticeship"
    ages = age_mix(data.rows)[-1]
    largest = max(ages.shares, key=lambda group: _number(ages.shares[group]))
    levy = funding_mix(data.rows)[-1].shares[LEVY]
    return Markdown(
        "## Key findings\n\n"
        f"- Starts {direction} by {abs(change):.1f}% between {first.year} and {last.year}.\n"
        f"- Higher apprenticeships were {levels[-1].shares[higher]:.1f}% of starts in "
        f"{last.year}, against {levels[0].shares[higher]:.1f}% in {first.year}.\n"
        f"- The largest age group in {last.year} was {largest}, with "
        f"{ages.shares[largest]:.1f}% of starts.\n"
        f"- {levy:.1f}% of starts in {last.year} were supported by levy funds."
    )


def over_time(data: ReportData) -> Html:
    """Return the trend in starts and achievements, and the mix of levels.

    Args:
        data: The report data.

    Returns:
        The section as HTML.
    """
    trend = national_trend(data.rows)
    first, last, latest = _window(data)
    caveat = f"{_source(data)} {latest} is left out because it covers August to April only."
    series = {
        "Starts": [(f.year, f.values["start_count"]) for f in trend],
        "Achievements": [(f.year, f.values["achievement_count"]) for f in trend],
    }
    starts, achievements = series["Starts"], series["Achievements"]
    summary = (
        f"Starts went from {starts[0][1]:,} in {first} to {starts[-1][1]:,} in {last}. "
        f"Achievements went from {achievements[0][1]:,} to {achievements[-1][1]:,}."
    )
    chart = line_chart(
        series,
        title="Starts and achievements",
        y_label="Number of starts and achievements",
        caveat=caveat,
        alt_text=summary,
    )
    levels = level_mix(data.rows)
    names = ["Intermediate Apprenticeship", "Advanced Apprenticeship", "Higher Apprenticeship"]
    mix = {name: [(m.year, m.shares[name]) for m in levels] for name in names}
    mix_summary = (
        f"The share of starts at higher level went from {mix[names[2]][0][1]:.1f}% in "
        f"{first} to {mix[names[2]][-1][1]:.1f}% in {last}."
    )
    mix_chart = line_chart(
        mix,
        title="Share of starts by level",
        y_label="Share of all starts (%)",
        caveat=f"{_source(data)} Shares are of all starts in each year.",
        alt_text=mix_summary,
    )
    return Html(
        "<h2>How have starts and achievements changed?</h2>"
        + _warning(NOT_A_RATE)
        + _figure(chart, summary, series)
        + "<h3>How has the mix of levels changed?</h3>"
        + _figure(mix_chart, mix_summary, mix, "{:.1f}%")
    )


def age_groups(data: ReportData) -> Html:
    """Return each age group's share of starts over time.

    Args:
        data: The report data.

    Returns:
        The section as HTML.
    """
    ages = age_mix(data.rows)
    groups = list(ages[-1].shares)
    series = {group: [(m.year, m.shares[group]) for m in ages] for group in groups}
    latest = ages[-1]
    parts = ", ".join(f"{g} made up {latest.shares[g]:.1f}% of starts" for g in groups)
    summary = f"In {latest.year}, {parts}."
    chart = line_chart(
        series,
        title="Share of starts by age group",
        y_label="Share of all starts (%)",
        caveat=f"{_source(data)} Age is age at the start of the apprenticeship (footnote 4).",
        alt_text=summary,
    )
    return Html(
        "<h2>Which age groups start apprenticeships?</h2>"
        + _figure(chart, summary, series, "{:.1f}%")
    )


def funding(data: ReportData) -> Html:
    """Return levy-funded and other starts as shares, from 2020/21.

    Args:
        data: The report data.

    Returns:
        The section as HTML.
    """
    mix = funding_mix(data.rows)
    series = {
        "Levy funded": [(m.year, m.shares[LEVY]) for m in mix],
        "Other": [(m.year, m.shares["Other"]) for m in mix],
    }
    summary = f"In {mix[-1].year}, {mix[-1].shares[LEVY]:.1f}% of starts were levy funded."
    chart = line_chart(
        series,
        title="Levy-funded and other starts",
        y_label="Share of all starts (%)",
        caveat=_source(data),
        alt_text=summary,
    )
    note = (
        "Why this starts in 2020/21: a minor amendment to how starts supported by levy "
        "funds are counted was applied for 2019/20, and a further one from 2020/21 "
        "(footnote 1), so 2020/21 is the first year counted on the current basis."
    )
    return Html(
        "<h2>How do levy-funded and other starts compare?</h2>"
        + _note(note)
        + _figure(chart, summary, series, "{:.1f}%")
    )

def regions(data: ReportData) -> Html:
    """Return the regions ranked by the share of their starts at higher level.

    Args:
        data: The report data.

    Returns:
        The section as HTML.
    """
    comparison = regional_comparison(data.rows)[-1]
    shares = {r.name: r.share for r in comparison.regions}
    top, bottom = comparison.regions[0], comparison.regions[-1]
    summary = (
        f"In {comparison.year}, {top.name} had the highest share of its starts at higher "
        f"level, at {_percent(top.share)}, and {bottom.name} the lowest, at "
        f"{_percent(bottom.share)}."
    )
    chart = bar_chart(
        shares,
        title=f"Share of each region's starts at higher level, {comparison.year}",
        x_label="Share of the region's starts (%)",
        caveat=(
            f"{_source(data)} Regions are ranked by share, so a large region does not "
            "rank higher just because it is large."
        ),
        alt_text=summary,
        value_format="{:.1f}%",
    )
    chart.figure.axes[0].margins(x=0.12)
    outside = (
        f"{comparison.outside.name} is not a region of England, so it is reported here "
        f"and not ranked: {_percent(comparison.outside.share)}. Suppressed cells in this "
        f"breakdown: {comparison.suppressed_cells}."
    )
    rows = "".join(
        f"<tr><td>{html.escape(name)}</td><td>{_percent(share)}</td></tr>"
        for name, share in shares.items()
    )
    return Html(
        "<h2>How do regions compare?</h2>"
        + _image(chart)
        + f"<p>{html.escape(summary)}</p><p>{html.escape(outside)}</p>"
        + "<details><summary>Show table</summary><table><tr><th>Region</th>"
        + f"<th>Share at higher level</th></tr>{rows}</table></details>"
    )


def about_the_data(data: ReportData) -> Html:
    """Return the reading notes and the data quality profile.

    Args:
        data: The report data.

    Returns:
        The section as HTML.
    """
    quality = profile(data.rows)
    markers = quality.suppressed_cells_by_marker
    granularity = suppression_by_granularity(data.rows)
    levy_z = "yes" if participation_z_in_all_levy_rows(data.rows) else "no"
    notes = [
        "Counts are rounded to the nearest 10, so totals may not add up exactly.",
        "Percentages are calculated on unrounded counts, so a share worked out from the "
        "rounded counts can differ slightly from the published one (footnote 8).",
        "The markers c, x, z and low replace figures that cannot be shown as numbers. "
        "They are never treated as zero.",
        f"{_window(data)[2]} covers August to April only, so it is left out.",
        NOT_A_RATE,
        "Participation counts learners, each once in the grand total, but a learner can "
        "appear under more than one level (footnotes 6 and 7).",
    ]
    profile_rows = [
        ("Rows loaded", f"{quality.rows_loaded:,}"),
        ("Pre-computed subtotal rows", f"{quality.subtotal_rows:,}"),
        *((f"Cells marked {m}", f"{markers.get(m, 0):,}") for m in ("c", "x", "z", "low")),
        ("low in count columns", f"{quality.low_in_count_columns:,}"),
        ("Participation is z in every levy-funded row", levy_z),
        *(
            (f"Cells suppressed with {level} filters", f"{share:.2f}%")
            for level, share in granularity.items()
        ),
    ]
    return Html(
        "<h2>About the data</h2><ul>"
        + "".join(f"<li>{html.escape(n)}</li>" for n in notes)
        + "</ul><h3>Data quality profile</h3>"
        + _table(("Measure", "Value"), profile_rows)
    )


def technical_notes(data: ReportData) -> Html:
    """Return the identifiers, versions, version history and known traps.

    Args:
        data: The report data.

    Returns:
        The section as HTML.
    """
    ordered = sort_versions(data.versions)
    history = []
    for older, newer in zip(ordered, ordered[1:], strict=False):
        changes = compare_schemas(data.schemas[str(older)], data.schemas[str(newer)])
        added = sorted(changes.added_filters | changes.added_indicators)
        removed = sorted(changes.removed_filters | changes.removed_indicators)
        text = "no change to filters or indicators"
        if changes.has_changes:
            text = f"added {_names(added)}, removed {_names(removed)}"
        history.append((f"{older} to {newer}", text))
    details = [
        ("Data set ID", DATA_SET_ID),
        ("Data set version", data.version),
        ("Pipeline version", __version__),
        ("Source code", REPOSITORY),
    ]
    return Html(
        "<h2>Technical notes</h2>"
        + _table(("Item", "Value"), details)
        + "<h3>Version history</h3>"
        + _table(("Versions", "Change"), history)
        + "<h3>Known traps in the data</h3><ul>"
        + "".join(f"<li>{html.escape(trap)}</li>" for trap in KNOWN_TRAPS)
        + "</ul>"
    )


def _window(data):
    """Return the first and last complete years, and the latest year left out."""
    years = sorted({normalise_time_period(row["time_period"]) for row in data.rows})
    return years[0], years[-2], years[-1]


def _source(data):
    """Return the caveat line's source, version and rounding."""
    return (
        f"Source: Explore Education Statistics, data set version {data.version}. "
        "Counts are rounded to the nearest 10."
    )


def _day(day):
    """Return a date written as, for example, 9 October 2026."""
    return f"{day.day} {day:%B %Y}"


def _number(value):
    """Return a value for comparison, treating a missing one as smallest."""
    return -1 if isinstance(value, Missing) else value


def _warning(text):
    """Return a warning box."""
    style = "border-left:6px solid #B25F00;background:#FFF7E0;padding:12px"
    return f'<div style="{style}"><strong>Warning:</strong> {html.escape(text)}</div>'


def _note(text):
    """Return a note box."""
    style = "border-left:6px solid #1D70B8;background:#EAF2F8;padding:12px"
    return f'<div style="{style}">{html.escape(text)}</div>'


def _image(chart: Chart) -> str:
    """Return a chart as an image with its alternative text, followed by its caveat.

    The bottom margin is widened first, so the caveat printed on the chart does
    not overlap the horizontal axis title.
    """
    chart.figure.subplots_adjust(bottom=0.2)
    buffer = io.BytesIO()
    chart.figure.savefig(buffer, format="png", dpi=110, bbox_inches="tight")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return (
        f'<img src="data:image/png;base64,{encoded}" alt="{html.escape(chart.alt_text)}">'
        f"<p><small>{html.escape(chart.caveat)}</small></p>"
    )


def _figure(chart, summary, series, value_format="{:,}"):
    """Return a chart, its written summary and a table of its values."""
    years = [year for year, _ in next(iter(series.values()))]
    head = "".join(f"<th>{html.escape(name)}</th>" for name in series)
    body = "".join(
        f"<tr><td>{year}</td>"
        + "".join(f"<td>{_cell(points[i][1], value_format)}</td>" for points in series.values())
        + "</tr>"
        for i, year in enumerate(years)
    )
    return (
        _image(chart)
        + f"<p><strong>In brief:</strong> {html.escape(summary)}</p>"
        + f"<details><summary>Show table</summary><table><tr><th>Year</th>{head}</tr>"
        + f"{body}</table></details>"
    )


def _cell(value, value_format):
    """Return one table cell's text, saying a missing value is not shown."""
    return "not shown" if isinstance(value, Missing) else value_format.format(value)


def _names(names):
    """Return column names joined with commas, or nothing if there are none."""
    return ", ".join(names) or "nothing"


def _percent(value):
    """Return a share as text, or say it is not shown."""
    return "not shown" if isinstance(value, Missing) else f"{value:.1f}%"


def _table(heading, rows):
    """Return a two-column HTML table."""
    head = "".join(f"<th>{html.escape(h)}</th>" for h in heading)
    body = "".join(
        f"<tr><td>{html.escape(str(a))}</td><td>{html.escape(str(b))}</td></tr>"
        for a, b in rows
    )
    return f"<table><tr>{head}</tr>{body}</table>"