# Sprint 1 review and retrospective

Sprint 1 ran from 28 September to 11 October 2026. Its goal was to build the data layer that the Sprint 2 report depends on: retrieving the data, parsing it safely and protecting every figure from the traps found in the real API responses. All nine issues were done by 6 October, five days before the sprint was due to end.

## Sprint review

| Issue | Points | Pull request |
|---|---|---|
| #1 Repository scaffolding, packaging and CI | 3 | #2 |
| #3 Indicator value parser for suppression markers | 3 | #10 |
| #11 Personas and empathy map for the report's users | 2 | #13 |
| #12 Wireframes and Figma prototype of the analysis report | 5 | #14 |
| #4 Time period normaliser | 2 | #15 |
| #5 Metadata model with namespaced identifiers | 3 | #16 |
| #6 Single-cell selector to prevent double counting | 3 | #17 |
| #7 Analysis window filter | 2 | #18 |
| #9 API client for data set endpoints | 5 | #19 |
| Total | 28 | |

The sprint delivered all 28 planned points. Every feature issue was built test first in two red-green cycles, and each pull request links the failing and passing CI runs that show it. The package now has 111 tests at 100% coverage.

The plan changed once during the sprint. I brought the design work, the personas in #11 and the wireframes and prototype in #12, forward into Sprint 1, so that the report built in Sprint 2 follows a design that has already been reviewed against its users. At the same time, version parsing and change detection in #8, worth 5 points, moved to Sprint 2.

The API client's tests replay responses I recorded from the live API on 6 October. Those recordings confirmed that the real summary, version list and CSV header match what the client expects.

## Retrospective

### What went well

Writing the tests first caught real problems before they reached `main`. The clearest case was in #9. Before error handling was added, a 404 whose body happened to be valid JSON was returned to the caller as if it were data, and the failing run in pull request #19 shows it.

The traps found in the real API responses translated directly into test cases. Examples include the identifier `mU59K` meaning two different things, the location code `z`, the three forms of the same academic year, and the subtotal rows that inflate a naive sum to four times the true total. Each trap is now covered by a test that would fail if the code stopped handling it.

The persona review of prototype version 1 produced nine concrete changes in version 2. The most significant was comparing regions by share instead of raw counts.

### What did not go well

Most of the problems came from creating and editing files by hand.

- In #4 the new module was created at the top level of the repository, not inside the package, and ruff reported an import-order error before any test ran.
- In #5 the new test file was not picked up at first. The sign was pytest collecting 44 tests when 53 were expected, and I caught it before committing.
- In #6 a pasted line kept trailing spaces and a blank line was missing, so ruff failed until both were fixed.

There were also slips in the GitHub workflow. After #5 merged, I removed the issue from the project board by accident through the Projects picker in its sidebar, which cleared its sprint, estimate and priority until I restored them. Pull request titles defaulted to the branch name twice, leaving #14 in lower case and #19 as "Api client". In #16, #18 and #19 the CI run links went in as bare addresses, not as links titled with the commit they belong to.

### Actions for Sprint 2

After creating any file, I will list its folder before running anything, and compare the number of tests pytest collects with the number expected. I will change an issue's board status only through its Status field, never through the Projects picker. When opening a pull request, I will set the title first. When adding run links, I will replace only the placeholder inside the brackets.