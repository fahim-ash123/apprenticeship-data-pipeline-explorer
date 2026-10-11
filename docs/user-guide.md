# User guide

This guide explains how to read the Apprenticeship Data Pipeline Explorer report and what it can and cannot tell you.

The report is published at https://fahim-ash123.github.io/apprenticeship-data-pipeline-explorer/ and is rebuilt every time a change is merged into `main`. Each build retrieves version 2.0.2 of the Department for Education's apprenticeships headline data set from the Explore Education Statistics API, and the header states the date it was retrieved.

## What the report covers

The analysis covers the academic years 2017/18 to 2024/25 for England, nationally and by region. It leaves out 2025/26, the latest year in the data, because that year is provisional and covers August to April only (footnote 12). The rule is to leave out the latest year, whatever it is, so the report stays correct when the publisher adds a new year.

## What each measure counts

- **Starts** count apprenticeships started during the year. A learner who starts more than one apprenticeship is counted more than once (footnote 11).
- **Achievements** count apprenticeships achieved during the year. A learner who achieves more than one is counted more than once (footnote 10).
- **Learners participating** counts learners, each once in the grand total. At level breakdowns a learner can appear under more than one level, so participation by level does not add up to the total (footnotes 6 and 7).

Dividing achievements by starts does not give an achievement rate. The two measures count different apprenticeships, and an apprenticeship achieved in one year may have started in an earlier one. The report repeats this warning beside the chart that shows both.

## The sections

1. **Header.** The data set version, the retrieval date and the analysis window.
2. **Key findings.** Four headline figures in plain language.
3. **How have starts and achievements changed?** The national trend, and each level's share of starts over time.
4. **Which age groups start apprenticeships?** Each age group's share of starts. Age is age at the start of the apprenticeship (footnote 4).
5. **How do levy-funded and other starts compare?** Shares from 2020/21 onwards. Footnote 1 records minor amendments to how levy-supported starts were counted for 2019/20 and from 2020/21, so 2020/21 is the first year counted on the current basis.
6. **How do regions compare?** Each region's share of its own starts at higher level, ranked. Shares are used instead of counts, so a large region does not rank higher just because it is large. "Outside of England and unknown" is reported separately and is not ranked.
7. **About the data.** Notes on reading the figures, and a profile of the suppressed and unavailable values.
8. **Technical notes.** The identifiers, versions, version history and known traps in the data.

## Reading the charts

Each chart uses the Okabe-Ito blue, vermillion and black, which stay distinct with red-green colour vision deficiency. Colour is never the only cue: each series also has its own line style and marker, and is labelled at the end of its line. The years affected by the pandemic, 2019/20 and 2020/21, are shaded.

Under each chart there is a caveat line with the source, the data set version and the rounding, a sentence headed "In brief" with the main figures, and a "Show table" list of every value. The caveat line also appears inside the chart image. The copy under the image is the one a screen reader can read.

## Limitations

- **Rounding.** Counts are rounded to the nearest 10, so totals may not add up exactly.
- **Published percentages.** These are calculated on unrounded counts (footnote 8). The shares in the report are worked out from the rounded counts, so they can differ from the published percentages by up to 0.1 percentage points.
- **Markers.** The markers c, x, z and low replace numbers that cannot be shown. The report never treats them as zero. In this data set, c appears only in the percentage columns, and low appears in count columns as well, although footnote 8 defines it only for percentages.
- **No per-capita figures.** The data set has no population figures, so the report gives no per-person rates.
- **Version history.** The version history compares the filters and indicators each version contains. It does not compare filter options or row counts, so a version that changed those shows as having no change to filters or indicators.