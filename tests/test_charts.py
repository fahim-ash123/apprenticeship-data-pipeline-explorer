"""Tests for the accessible charts.

Each test draws a chart from a few made-up points and inspects the figure, so
the checks cover what a reader sees: the title, axis titles, line styles,
markers, direct labels and caveat line.
"""

import math

import pytest
from matplotlib.text import Annotation

from apprenticeship_explorer.charts import (
    BLUE,
    NOT_SHOWN,
    SERIES_STYLES,
    VERMILLION,
    bar_chart,
    contrast_ratio,
    line_chart,
)
from apprenticeship_explorer.parse import parse_indicator_value
from apprenticeship_explorer.time_period import AcademicYear

CAVEAT = "Source: Explore Education Statistics, data set version 2.0.2. Rounded to the nearest 10."
ALT = "Starts fell from 375,760 in 2017/18 to 353,500 in 2024/25."


def two_series():
    """Return starts and achievements for three years."""
    years = [AcademicYear(2017), AcademicYear(2018), AcademicYear(2019)]
    return {
        "Starts": list(zip(years, [375760, 393380, 322530], strict=True)),
        "Achievements": list(zip(years, [276160, 185150, 146900], strict=True)),
    }


def draw(series=None, **overrides):
    """Draw a line chart with sensible defaults for anything not given."""
    settings = {"title": "Starts and achievements", "y_label": "Number of starts and achievements"}
    settings.update(caveat=CAVEAT, alt_text=ALT)
    settings.update(overrides)
    return line_chart(series or two_series(), **settings)


def test_chart_has_a_title_and_axis_titles_naming_the_measure():
    """The title and both axis titles are set, and the vertical one names the measure."""
    axes = draw().figure.axes[0]
    assert axes.get_title(loc="left") == "Starts and achievements"
    assert axes.get_xlabel() == "Academic year"
    assert axes.get_ylabel() == "Number of starts and achievements"


def test_caveat_is_printed_on_the_chart():
    """The source, version and rounding appear under the chart, not only beside it."""
    chart = draw()
    assert [text.get_text() for text in chart.figure.texts] == [CAVEAT]
    assert chart.caveat == CAVEAT


def test_chart_carries_its_alternative_text():
    """The description for screen readers travels with the chart."""
    assert draw().alt_text == ALT


@pytest.mark.parametrize("missing", ["alt_text", "caveat"])
def test_chart_without_alternative_text_or_caveat_is_refused(missing):
    """A chart cannot be drawn without the text that makes it accessible."""
    with pytest.raises(ValueError):
        draw(**{missing: "  "})


def test_series_differ_by_line_style_and_marker_as_well_as_colour():
    """Blue is solid with circles and vermillion is dashed with squares."""
    lines = draw().figure.axes[0].get_lines()
    styles = [(line.get_color(), line.get_linestyle(), line.get_marker()) for line in lines]
    assert styles == [(BLUE, "-", "o"), (VERMILLION, "--", "s")]


def test_every_series_is_labelled_at_the_end_of_its_line():
    """Each label sits beside the last point of its own line, so no colour key is needed."""
    axes = draw().figure.axes[0]
    labels = {text.get_text(): text.xy for text in axes.texts if isinstance(text, Annotation)}
    assert labels == {"Starts": (2, 322530), "Achievements": (2, 146900)}


def test_years_are_shown_in_the_published_form():
    """The horizontal axis reads 2017/18, 2018/19 and 2019/20."""
    axes = draw().figure.axes[0]
    assert [tick.get_text() for tick in axes.get_xticklabels()] == ["2017/18", "2018/19", "2019/20"]


def test_missing_value_leaves_a_gap_not_a_zero():
    """A suppressed value is drawn as a break in the line."""
    series = two_series()
    series["Starts"][1] = (series["Starts"][1][0], parse_indicator_value("c"))
    starts = draw(series).figure.axes[0].get_lines()[0]
    assert math.isnan(starts.get_ydata()[1])


def test_more_series_than_styles_is_refused():
    """A fourth series would have to reuse a style, so it is not drawn."""
    year = AcademicYear(2017)
    series = {f"Series {n}": [(year, n)] for n in range(4)}
    with pytest.raises(ValueError, match="3 series"):
        draw(series)


@pytest.mark.parametrize("colour", [style[0] for style in SERIES_STYLES])
def test_every_series_colour_meets_the_3_to_1_contrast_minimum(colour):
    """WCAG 2.2 asks for 3:1 between a graphic and its background."""
    assert contrast_ratio(colour) >= 3


def eight_years():
    """Return one series covering 2017/18 to 2024/25, which includes the pandemic years."""
    years = [AcademicYear(y) for y in range(2017, 2025)]
    return {"Starts": [(year, 300000 + 1000 * n) for n, year in enumerate(years)]}


def test_pandemic_years_are_shaded_and_labelled():
    """2019/20 and 2020/21 are marked, so a dip is read in context, not removed."""
    axes = draw(eight_years()).figure.axes[0]
    assert "Pandemic-affected years" in [text.get_text() for text in axes.texts]
    assert len(axes.patches) == 1
    assert len(axes.get_lines()[0].get_xdata()) == 8


def test_no_pandemic_shading_when_those_years_are_not_shown():
    """A chart from 2021/22 onwards has nothing to shade."""
    years = [AcademicYear(2021), AcademicYear(2022)]
    axes = draw({"Starts": [(years[0], 1), (years[1], 2)]}).figure.axes[0]
    assert len(axes.patches) == 0
    assert "Pandemic-affected years" not in [text.get_text() for text in axes.texts]


def draw_bars(values=None, **overrides):
    """Draw a bar chart of regional shares with sensible defaults."""
    settings = {"title": "Share of starts at higher level", "x_label": "Share of starts (%)"}
    settings.update(caveat=CAVEAT, alt_text=ALT, value_format="{:.1f}%")
    settings.update(overrides)
    shares = {"London": 50.5, "East of England": 42.3, "South East": 40.7}
    return bar_chart(values or shares, **settings)


def test_bars_keep_the_order_given_from_top_to_bottom():
    """A ranked list stays ranked: the first label is the top bar."""
    axes = draw_bars().figure.axes[0]
    names = [tick.get_text() for tick in axes.get_yticklabels()]
    ticks = zip(axes.get_yticks(), names, strict=True)
    top_down = [label for _, label in sorted(ticks, reverse=True)]
    assert top_down == ["London", "East of England", "South East"]


def test_every_bar_is_labelled_with_its_value():
    """Values are printed beside the bars, so the chart can be read without the axis."""
    texts = [text.get_text().strip() for text in draw_bars().figure.axes[0].texts]
    assert texts == ["50.5%", "42.3%", "40.7%"]


def test_bar_chart_has_title_axis_title_and_caveat():
    """The bar chart carries the same text as the line chart."""
    chart = draw_bars()
    axes = chart.figure.axes[0]
    assert axes.get_title(loc="left") == "Share of starts at higher level"
    assert axes.get_xlabel() == "Share of starts (%)"
    assert [text.get_text() for text in chart.figure.texts] == [CAVEAT]


def test_suppressed_bar_is_shown_as_not_available():
    """A missing value is stated in words, never drawn as an empty bar."""
    values = {"London": parse_indicator_value("c"), "South East": 40.7}
    axes = draw_bars(values).figure.axes[0]
    assert len(axes.patches) == 1
    assert NOT_SHOWN in [text.get_text() for text in axes.texts]


def test_bar_chart_without_alternative_text_is_refused():
    """The bar chart enforces the same accessibility text as the line chart."""
    with pytest.raises(ValueError):
        draw_bars(alt_text="")    