"""Tests for the package as a whole."""

import apprenticeship_explorer


def test_package_exposes_a_version():
    """The package reports the version declared in pyproject.toml."""
    assert apprenticeship_explorer.__version__ == "0.1.0"