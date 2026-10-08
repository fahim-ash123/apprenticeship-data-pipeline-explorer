# Sprint 2 plan

Sprint 2 runs from 7 to 11 October 2026. Sprint 1 was planned to end on 11 October, but all its work was done by 6 October, so I closed it that day and started Sprint 2 early. The period from 12 to 18 October is kept for revising the report and submitting it, and is not part of any sprint.

## Sprint goal

Turn the tested data layer into a published report: compute the metrics the report needs, draw them as accessible charts, lay them out in a notebook that follows prototype version 2, publish the result to GitHub Pages, and document how to use and maintain it.

## Capacity

Sprint 1 delivered 28 points. The Sprint 2 backlog as first planned came to 36 points, including the version parsing issue moved from Sprint 1. Committing to 36 points in a five-day sprint would have exceeded the velocity Sprint 1 showed, so I committed to 29 points and moved two issues to the backlog as future work.

| Issue | Points | Priority |
|---|---|---|
| #8 Version parsing, ordering and change detection | 5 | Medium |
| National trend metrics | 3 | High |
| Level and age mix metrics | 3 | High |
| Regional comparison by within-region share | 3 | Medium |
| Data quality profile | 3 | Medium |
| Accessible charts | 3 | High |
| Analysis notebook | 3 | High |
| Report build and deployment to GitHub Pages | 3 | High |
| User and technical documentation | 3 | High |
| Total | 29 | |

## Descoped to the backlog

| Issue | Points | Reason |
|---|---|---|
| Naive achievement ratio demonstration | 5 | The persona review asked for a warning beside the charts that invite dividing achievements by starts, which the notebook delivers. A full demonstration of lagged ratios goes further than any persona needs. |
| Percentage denominator verification | 2 | No section of the report depends on the published percentages. |

## Persona review changes

Each change from the review of prototype version 1 is delivered by a Sprint 2 issue.

| Review item | Change | Delivered by |
|---|---|---|
| R1 | "Not an achievement rate" warning beside paired charts | Analysis notebook |
| R2 | Caveat line with source, version and rounding under every chart | Accessible charts |
| R3 | Reason for leaving out 2025/26 stated under the trend chart | Analysis notebook |
| R4 | Each level's share of all starts over time | Level and age mix metrics |
| R5 | Axis titles and series named by the measure, never "learners" | National trend metrics, Accessible charts |
| R6 | Regions compared by share, not raw counts | Regional comparison by within-region share |
| R7 | Suppressed cells counted and shown in breakdowns | Regional comparison by within-region share |
| R8 | Data quality profile | Data quality profile |
| R9 | Version history and known traps in the technical notes | Analysis notebook, with #8 providing the version comparison |

The Definition of Ready and Definition of Done are unchanged from Sprint 1.