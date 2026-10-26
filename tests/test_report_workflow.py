"""Tests for the workflow that builds and publishes the report.

The workflow is read as text, because what matters is its contract: it runs
only after CI has passed on a push to ``main``, it builds the notebook with
nbconvert, and it publishes the page with GitHub Pages.
"""

from pathlib import Path

ROOT = Path(__file__).parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "report.yml"
REPORT_ADDRESS = "https://fahim-ash123.github.io/apprenticeship-data-pipeline-explorer/"


def workflow():
    """Return the report workflow's text."""
    return WORKFLOW.read_text()


def test_runs_when_ci_finishes_on_main():
    """The report is built after the CI workflow completes for ``main``."""
    text = workflow()
    assert "workflow_run:" in text
    assert "workflows: [CI]" in text
    assert "branches: [main]" in text


def test_publishes_only_after_ci_passed_on_a_push():
    """A failed CI run, or a run for a pull request, never publishes the report."""
    text = workflow()
    assert "github.event.workflow_run.conclusion == 'success'" in text
    assert "github.event.workflow_run.event == 'push'" in text
    assert "ref: ${{ github.event.workflow_run.head_sha }}" in text


def test_builds_the_notebook_with_nbconvert():
    """The page is the executed notebook without its code, saved as the site's index."""
    text = workflow()
    assert "jupyter nbconvert --to html --execute --no-input notebooks/report.ipynb" in text
    assert "--output-dir build --output index" in text


def test_deploys_with_github_pages():
    """The built page is uploaded and deployed with GitHub's Pages actions."""
    text = workflow()
    assert "actions/upload-pages-artifact@v5" in text
    assert "actions/deploy-pages@v5" in text
    assert "pages: write" in text
    assert "id-token: write" in text


def test_readme_gives_the_report_address():
    """Readers can find the published report from the README."""
    assert REPORT_ADDRESS in (ROOT / "README.md").read_text()


def test_publishes_the_coverage_figure_beside_the_report():
    """The tests run again in the build, writing their coverage as JSON for the badge."""
    text = workflow()
    assert 'python -m pip install -e ".[dev,report]" -c constraints.txt' in text
    assert "pytest --cov-report=json:build/coverage.json" in text


def test_readme_shows_a_coverage_badge_read_from_the_published_figure():
    """The badge reads the percentage from the coverage file published with the report."""
    readme = (ROOT / "README.md").read_text()
    assert "img.shields.io/badge/dynamic/json" in readme
    assert "coverage.json" in readme