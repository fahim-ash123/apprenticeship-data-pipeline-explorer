"""Draw the report's charts so they can be read without relying on colour.

The palette is the Okabe-Ito blue, vermillion and black, which stay distinct
with red-green colour vision deficiency. Colour is never the only cue: each
series also has its own line style and marker, and is labelled at the end of
its line. Every chart carries a title, axis titles naming the measure, a
caveat line with the source, version and rounding, and alternative text.
"""

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from matplotlib.figure import Figure

from apprenticeship_explorer.parse import Missing
from apprenticeship_explorer.time_period import AcademicYear

BLUE, VERMILLION, BLACK = "#0072B2", "#D55E00", "#000000"
SERIES_STYLES = ((BLUE, "-", "o"), (VERMILLION, "--", "s"), (BLACK, ":", "D"))
TEXT, CAVEAT_TEXT = "#1A1A1A", "#505A5F"
PANDEMIC_YEARS = (AcademicYear(2019), AcademicYear(2020))
NOT_SHOWN = "Not shown: suppressed or unavailable"


@dataclass(frozen=True)
class Chart:
    """A chart with the text a reader needs alongside it.

    Attributes:
        figure: The matplotlib figure.
        alt_text: A description of what the chart shows, for screen readers.
        caveat: The source, version and rounding, also printed under the chart.
    """

    figure: Figure
    alt_text: str
    caveat: str


def line_chart(
    series: Mapping[str, Sequence[tuple[AcademicYear, object]]],
    *,
    title: str,
    y_label: str,
    caveat: str,
    alt_text: str,
) -> Chart:
    """Draw up to three series over academic years.

    Args:
        series: Each series' label mapped to its ``(year, value)`` points. A
            missing value leaves a gap in the line, never a zero.
        title: The chart title.
        y_label: The vertical axis title, naming the measure.
        caveat: The source, version and rounding.
        alt_text: A description of the chart for screen readers.

    Returns:
        The chart.

    Raises:
        ValueError: If there are more series than styles, or the alternative
            text or caveat is empty.
    """
    _check_text(alt_text, caveat)
    if len(series) > len(SERIES_STYLES):
        raise ValueError(f"At most {len(SERIES_STYLES)} series can be told apart")
    years = sorted({year for points in series.values() for year, _ in points})
    position = {year: index for index, year in enumerate(years)}
    figure = Figure(figsize=(9, 5))
    axes = figure.add_subplot()
    for (label, points), (colour, style, marker) in zip(
        series.items(), SERIES_STYLES, strict=False
    ):
        xs = [position[year] for year, _ in points]
        ys = [math.nan if isinstance(value, Missing) else value for _, value in points]
        axes.plot(xs, ys, color=colour, linestyle=style, marker=marker, linewidth=2.5)
        known = [(x, y) for x, y in zip(xs, ys, strict=True) if not math.isnan(y)]
        if known:
            axes.annotate(
                label,
                known[-1],
                xytext=(8, 0),
                textcoords="offset points",
                va="center",
                color=TEXT,
                fontweight="bold",
            )
    axes.set_xticks(range(len(years)), [str(year) for year in years])
    axes.set_title(title, loc="left", color=TEXT, fontweight="bold")
    axes.set_xlabel("Academic year", color=TEXT)
    axes.set_ylabel(y_label, color=TEXT)
    figure.text(0.01, 0.01, caveat, fontsize=9, color=CAVEAT_TEXT)
    return Chart(figure, alt_text, caveat)

def bar_chart(
    values: Mapping[str, object],
    *,
    title: str,
    x_label: str,
    caveat: str,
    alt_text: str,
    value_format: str = "{:,.0f}",
) -> Chart:
    """Draw horizontal bars, top to bottom in the order given, each labelled with its value.

    Args:
        values: Each bar's label mapped to its value. A missing value is shown
            as not available instead of as an empty bar.
        title: The chart title.
        x_label: The horizontal axis title, naming the measure.
        caveat: The source, version and rounding.
        alt_text: A description of the chart for screen readers.
        value_format: How each value is printed beside its bar, such as
            ``{:.1f}%`` for a share.

    Returns:
        The chart.

    Raises:
        ValueError: If the alternative text or caveat is empty.
    """
    # Deliberately not implemented yet. The tests are written first.
    raise NotImplementedError


def contrast_ratio(colour: str, background: str = "#FFFFFF") -> float:
    """Return the WCAG 2.2 contrast ratio between two hex colours.

    Args:
        colour: A colour such as ``#0072B2``.
        background: The background colour, white by default.

    Returns:
        The ratio, from 1 for identical colours to 21 for black on white.
    """
    lighter, darker = sorted((_luminance(colour), _luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def _luminance(colour: str) -> float:
    """Return a hex colour's relative luminance, as WCAG 2.2 defines it.

    Args:
        colour: A colour such as ``#0072B2``.

    Returns:
        The relative luminance, from 0 for black to 1 for white.
    """
    channels = [int(colour[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _check_text(alt_text: str, caveat: str) -> None:
    """Refuse to draw a chart without its alternative text and caveat.

    Args:
        alt_text: The chart's alternative text.
        caveat: The chart's caveat line.

    Raises:
        ValueError: If either is empty.
    """
    if not alt_text.strip():
        raise ValueError("Every chart needs alternative text")
    if not caveat.strip():
        raise ValueError("Every chart needs a caveat line")