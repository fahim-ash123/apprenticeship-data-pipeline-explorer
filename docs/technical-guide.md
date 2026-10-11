# Technical guide

This guide explains how to install, test and build the Apprenticeship Data Pipeline Explorer, and how its automation works.

## Requirements

- Python 3.13
- Internet access to `https://api.education.gov.uk`, needed only to build the report, not to run the tests

## Installing

The project is a Python package with two optional dependency groups: `dev` for the test and lint tools, and `report` for building the notebook. Every package is pinned to an exact version in `constraints.txt`.

In a GitHub Codespace, the dev container installs everything when the codespace is created. To install anywhere else, from the repository's top-level folder:

```
python -m pip install -e ".[dev,report]" -c constraints.txt
```

## Running the tests and the linter

```
ruff check 
```
```
pytest
```

`pytest` reports coverage for every module in `src/apprenticeship_explorer`. No test calls the live API: tests that need API responses replay files recorded in `tests/fixtures`, through a fake transport.

## Building the report locally

```
jupyter nbconvert --to html --execute --no-input notebooks/report.ipynb --output-dir build
```

This runs the notebook against the live API and writes `build/report.html`. The `build` folder is ignored by git.

## Recording fixtures

The fixtures are real API responses, trimmed where they would otherwise be large. `tests/fixtures/README.md` records the source and date of each one. To record a new fixture, download it with `curl` and add a line to that README. Do not use `curl --compressed` for the CSV without testing the client against a compressed response, because the live CSV endpoint sends its body gzip-compressed (issue #42).

## Automation

- **CI**, in `.github/workflows/ci.yml`, runs on every push and pull request. It installs the package with the `dev` group, then runs `ruff check .` and `pytest`. The `main` branch is protected, so a pull request can only be merged when CI has passed.
- **Report**, in `.github/workflows/report.yml`, runs when CI completes on `main`, and only if CI succeeded on a push, which is what a merge is. It checks out the commit that passed, builds the notebook with nbconvert, and publishes the page to GitHub Pages.

## Working practice

Each change follows one issue, one branch and one pull request. Features are built test first, with the failing and passing CI runs linked from the pull request. Bugs use the bug template, which records the reproduction, the evidence, the root cause and the regression test. Pull requests are merged with a merge commit, so the branch history stays visible.

## Adding a section to the report

1. Write a function in `src/apprenticeship_explorer/report.py` that takes `ReportData` and returns `Html` or `Markdown`, with tests in `tests/test_report.py`.
2. Add its name to `SECTIONS` in the order it should appear.
3. Add a code cell to `notebooks/report.ipynb` that calls it, such as `report.new_section(data)`.

The notebook tests fail if the cells do not match `SECTIONS`, or if a cell contains anything other than a call to the package.