"""Draw the report's charts so they can be read without relying on colour.

The palette is the Okabe-Ito blue, vermillion and black, which stay distinct
with red-green colour vision deficiency. Colour is never the only cue: each
series also has its own line style and marker, and is labelled at the end of
its line. Every chart carries a title, axis titles naming the measure, a
caveat line with the source, version and rounding, and alternative text.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from matplotlib.figure import Figure

from apprenticeship_explorer.time_period import AcademicYear

BLUE, VERMILLION, BLACK = "#0072B2", "#D55E00", "#000000"
SERIES_STYLES = ((BLUE, "-", "o"), (VERMILLION, "--", "s"), (BLACK, ":", "D"))
TEXT, CAVEAT_TEXT = "#1A1A1A", "#505A5F"


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
    raise NotImplementedError