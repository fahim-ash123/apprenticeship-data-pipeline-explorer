"""Tests for the report sections.

The sections are built from the recorded national breakdown and regional
fixtures, which hold real version 2.0.2 rows, so the expected figures are the
published ones. The retrieval date is fixed, so the header can be checked.
"""

import csv
import json
from datetime import date
from pathlib import Path

from apprenticeship_explorer import report
from apprenticeship_explorer.client import ApiClient, Response

FIXTURES = Path(__file__).parent / "fixtures"
NOTEBOOK = Path(__file__).parent.parent / "notebooks" / "report.ipynb"
RETRIEVED = date(2026, 10, 9)


def recorded_rows():
    """Return the recorded national breakdown and regional rows together."""
    rows = []
    for name in ("national-breakdowns.csv", "regional-levels.csv"):
        with open(FIXTURES / name, encoding="utf-8-sig", newline="") as file:
            rows.extend(csv.DictReader(file))
    return rows


def recorded_schemas():
    """Return the recorded metadata for versions 1.0, 1.0.1 and 2.0.2."""
    versions = ("1.0", "1.0.1", "2.0.2")
    return {v: json.loads((FIXTURES / f"meta-{v}.json").read_text()) for v in versions}


def report_data():
    """Return report data built from the fixtures."""
    schemas = recorded_schemas()
    return report.ReportData(recorded_rows(), "2.0.2", RETRIEVED, list(schemas), schemas)


class FakeTransport:
    """Return queued responses in order and record each URL requested."""

    def __init__(self, *bodies):
        """Queue the response bodies."""
        self.bodies = list(bodies)
        self.urls = []

    def __call__(self, url, timeout):
        """Record the request and return the next body as a 200 response."""
        self.urls.append(url)
        return Response(200, self.bodies.pop(0))


def test_load_pins_the_version_and_fetches_every_schema():
    """The CSV is fetched for the pinned version, then the metadata for each version."""
    csv_text = b"time_period,start_count\n202425,353500\n"
    versions = b'{"paging": {"totalPages": 1}, "results": [{"version": "1.0"}, {"version": "2.0"}]}'
    transport = FakeTransport(csv_text, versions, b'{"filters": []}', b'{"filters": [1]}')
    data = report.load(ApiClient(transport), today=RETRIEVED)
    assert transport.urls[0].endswith("/csv?dataSetVersion=2.0.2")
    assert data.rows == [{"time_period": "202425", "start_count": "353500"}]
    assert data.versions == ["1.0", "2.0"]
    assert data.schemas == {"1.0": {"filters": []}, "2.0": {"filters": [1]}}
    assert data.retrieved == RETRIEVED


def test_header_states_version_retrieval_date_and_window():
    """The reader sees which data was used, when it was fetched and which years it covers."""
    text = report.header(report_data())
    assert "Data set version 2.0.2, retrieved 9 October 2026." in text
    assert "covers 2017/18 to 2024/25" in text
    assert "leaves out 2025/26" in text
    assert "August to April only (footnote 12)" in text


def test_key_findings_are_the_published_figures():
    """Each finding is worked out from the recorded rows, not typed in."""
    text = report.key_findings(report_data())
    assert "Starts fell by 5.9% between 2017/18 and 2024/25." in text
    assert "Higher apprenticeships were 39.8% of starts in 2024/25" in text
    assert "against 12.8% in 2017/18." in text
    assert "The largest age group in 2024/25 was 25 plus, with 51.3% of starts." in text
    assert "68.8% of starts in 2024/25 were supported by levy funds." in text


def test_trend_has_the_not_a_rate_warning_beside_it():
    """Starts and achievements share a chart, so the warning sits with it (R1)."""
    assert "This is not an achievement rate." in report.over_time(report_data())


def test_trend_caveat_says_why_2025_26_is_left_out():
    """The reason for leaving out the latest year is under the trend chart (R3)."""
    text = report.over_time(report_data())
    assert "2025/26 is left out because it covers August to April only." in text


def test_trend_summary_gives_the_first_and_last_figures():
    """The written summary is the chart's text alternative, so it holds the real numbers."""
    text = report.over_time(report_data())
    assert "Starts went from 375,760 in 2017/18 to 353,500 in 2024/25." in text
    assert "Achievements went from 276,160 to 198,330." in text


def test_charts_are_images_with_alternative_text_and_a_table():
    """Each chart is an image whose alt text is its summary, with its values in a table."""
    text = report.over_time(report_data())
    assert 'alt="Starts went from 375,760' in text
    assert text.count("<details><summary>Show table</summary>") == 2


def test_age_section_gives_each_group_and_the_footnote():
    """The age mix states every group's share and that age is age at the start."""
    text = report.age_groups(report_data())
    assert "25 plus made up 51.3% of starts" in text
    assert "age at the start of the apprenticeship (footnote 4)" in text


def test_funding_section_starts_in_2020_21_and_says_why():
    """The note cites footnote 1, and the table's first year is 2020/21."""
    text = report.funding(report_data())
    assert "(footnote 1)" in text
    assert "<tr><td>2020/21</td>" in text
    assert "<tr><td>2019/20</td>" not in text
    assert "68.8% of starts were levy funded" in text


def test_sections_display_in_a_notebook():
    """Each section knows how the notebook should show it."""
    data = report_data()
    assert report.header(data)._repr_markdown_().startswith("# Apprenticeship")
    assert report.funding(data)._repr_html_().startswith("<h2>")

def test_regions_section_names_the_highest_and_lowest_shares():
    """London leads at 50.5% in 2024/25 and Yorkshire and The Humber is lowest at 33.7%."""
    text = report.regions(report_data())
    assert "London had the highest share of its starts at higher level, at 50.5%" in text
    assert "Yorkshire and The Humber the lowest, at 33.7%" in text


def test_regions_section_reports_outside_england_and_suppression():
    """The outside region is reported apart, with the count of suppressed cells (R7)."""
    text = report.regions(report_data())
    assert "Outside of England and unknown is not a region of England" in text
    assert "52.2%" in text
    assert "Suppressed cells in this breakdown: 0." in text


def test_about_the_data_includes_the_quality_profile():
    """The profile states the rows loaded and the levy participation check (R8)."""
    data = report_data()
    text = report.about_the_data(data)
    assert f"<td>Rows loaded</td><td>{len(data.rows):,}</td>" in text
    assert "<td>Participation is z in every levy-funded row</td><td>yes</td>" in text
    assert "This is not an achievement rate." in text


def test_technical_notes_give_the_version_history():
    """Comparing each version with the next shows the filter added in 1.0.1 (R9)."""
    text = report.technical_notes(report_data())
    assert "<td>1.0 to 1.0.1</td><td>added age_youth_adult, removed nothing</td>" in text
    assert "<td>1.0.1 to 2.0.2</td><td>no change to filters or indicators</td>" in text


def test_technical_notes_list_every_known_trap():
    """Each trap found in the real data is listed for the next analyst."""
    text = report.technical_notes(report_data())
    assert all(f"<li>{trap}</li>" in text for trap in report.KNOWN_TRAPS)
    assert report.DATA_SET_ID in text


def notebook_code():
    """Return the source of each code cell in the report notebook."""
    cells = json.loads(NOTEBOOK.read_text())["cells"]
    return ["".join(cell["source"]) for cell in cells if cell["cell_type"] == "code"]


def test_notebook_imports_only_the_package():
    """The notebook holds no analytical logic, so it imports nothing but the report."""
    imports = [
        line for cell in notebook_code() for line in cell.splitlines()
        if line.startswith(("import ", "from "))
    ]
    assert imports == ["from apprenticeship_explorer import report"]


def test_notebook_has_no_logic_of_its_own():
    """No cell defines a function or class, or loops, so every calculation is tested code."""
    words = ("def ", "class ", "for ", "while ", "lambda")
    assert not any(word in cell for cell in notebook_code() for word in words)


def test_notebook_shows_every_section_in_the_prototype_order():
    """The sections run in the order of prototype version 2."""
    calls = [cell.strip() for cell in notebook_code()[2:]]
    assert calls == [f"report.{section}(data)" for section in report.SECTIONS]