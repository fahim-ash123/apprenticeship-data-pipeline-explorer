# Sprint 2 review and retrospective

Sprint 2 ran from 7 to 11 October 2026. It started early because Sprint 1 finished on 6 October, five days ahead of its planned end. Its goal was to turn the tested data layer into a published report: compute the metrics, draw them as accessible charts, lay them out in a notebook following prototype version 2, publish the result to GitHub Pages, and document how to use and maintain it.

## Sprint review

| Issue | Points | Pull request |
|---|---|---|
| #8 Version parsing, ordering and change detection | 5 | #34 |
| #23 National trend metrics | 3 | #35 |
| #24 Level and age mix metrics | 3 | #36 |
| #25 Regional comparison by within-region share | 3 | #39 |
| #26 Data quality profile | 3 | #40 |
| #27 Accessible charts | 3 | #41 |
| #28 Analysis notebook | 3 | #44 |
| #29 Report build and deployment to GitHub Pages | 3 | #45 |
| #30 User and technical documentation | 3 | #46 |
| Planned total | 29 | |
| #37 Participation is wrongly described as not counting learners, bug | 1 | #38 |
| #42 CSV download fails because the API sends it gzip-compressed, bug | 1 | #43 |
| #47 Report wording says "1 filters" and overstates the version history, bug | 1 | #48 |
| Delivered total | 32 | |

The sprint delivered all 29 planned points and 3 unplanned points of bug fixes, 32 in all. At planning, the backlog for Sprint 2 came to 36 points. I committed to 29, close to Sprint 1's velocity of 28, and moved two issues to the backlog: the naive achievement ratio demonstration (#31, 5 points) and the percentage denominator verification (#32, 2 points). Both remain there as future work.

The report is published at https://fahim-ash123.github.io/apprenticeship-data-pipeline-explorer/ and is rebuilt from the live API every time a change is merged into `main`, only after CI has passed. The package has 232 tests at 100% coverage.

## Findings from the real data

Building against real responses, and then running the report on all 51,298 rows of version 2.0.2, produced findings that the earlier exploration had not:

- The age group rows sit under the youth or adult split. A row for 19 to 24 carries `age_youth_adult` as 19 plus, not Total, so a selection with every other filter at Total finds no row.
- 2017/18 has a fourth level, Unknown, whose counts are all `low`.
- The `c` marker never appears in a count column, only in the two percentage columns. Small counts are shown as `low` instead, 23,899 times, although footnote 8 defines `low` only for percentages.
- The `x` marker never appears, although footnote 8 defines it.
- Suppression rises with granularity, from none of the cells at the grand total to 15.81% at four filters.
- In 2024/25, London has the highest share of its starts at higher level, 50.5%, while the South East has the most higher-level starts by count. Ranking by share instead of count was the change persona review item R6 asked for.
- A share worked out from the rounded counts can differ from the published percentage, because footnote 8 says percentages use unrounded counts. The West Midlands comes to 39.15% and is published as 39.1%.

## Retrospective

### What went well

Testing against recorded real responses kept paying off. Each data trap became a test that would fail if the code stopped handling it, and the nested age rows and the Unknown level were caught by tests built on real rows before any chart was drawn.

Capacity planning held. Committing to 29 points against a velocity of 28, with two issues moved to the backlog, left room for three unplanned bugs inside a five-day sprint.

Each bug went through the bug template with a failing regression test first. That made the three bugs a visible record, not quiet fixes.

The deployment rule works as designed. The report workflow only runs after CI passes on a push to `main`, and the first deployment followed the merge of #45 without anyone running anything by hand.

### What did not go well

The most serious problem was a test fixture that hid a bug. The CSV fixture in #9 was recorded with `curl --compressed`, which decompresses the file before saving it. So every test replayed the uncompressed form, while the live API sends the CSV gzip-compressed. The fault only appeared when the notebook first ran against the live API in #28, and it became bug #42.

I also made a false claim in code. When building #23, I applied footnotes 10 and 11, which cover starts and achievements, to participation as well, without checking footnote 7. A test then enforced the wrong rule. This became bug #37.

The workflow slips from Sprint 1 recurred in new forms:

- The fixture for #24 was left out of the commits, because a staged step was skipped. The first four CI runs on that branch failed for that reason, and I rebuilt the branch with the fixture as its first commit.
- A bug issue number was carried wrongly into the pull request for #42, which said `Closes #46`. So the issue did not close automatically, and I corrected the record by hand.
- A wording error, "1 filters", and an overstated version history line reached the published report. These became bug #47.

### Lessons for future work

Fixtures should be recorded exactly as the client receives them, using the same transport the code uses, so the tests cannot replay something the live service never sends. Running the product end to end against the live service should happen as soon as there is something to run, not only at the end. `git status` before every commit, which I adopted after #24, caught every later omission. Finally, the version history compares filters and indicators only. Comparing filter options and row counts between versions would make it complete, and is the clearest next feature alongside the two backlog issues.