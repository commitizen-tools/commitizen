from __future__ import annotations

import pytest

from commitizen.version_increment import VersionIncrement


@pytest.mark.parametrize(
    ("increment", "expected_value"),
    [
        (VersionIncrement.NONE, 0),
        (VersionIncrement.PATCH, 1),
        (VersionIncrement.MINOR, 2),
        (VersionIncrement.MAJOR, 3),
    ],
)
def test_version_increment_enum_values(increment, expected_value):
    """Test that all VersionIncrement enum values are correctly defined."""
    assert increment == expected_value


@pytest.mark.parametrize(
    ("increment", "expected_name"),
    [
        (VersionIncrement.NONE, "NONE"),
        (VersionIncrement.PATCH, "PATCH"),
        (VersionIncrement.MINOR, "MINOR"),
        (VersionIncrement.MAJOR, "MAJOR"),
    ],
)
def test_version_increment_str(increment, expected_name):
    """Test that __str__ returns the enum name."""
    assert str(increment) == expected_name


@pytest.mark.parametrize(
    ("value", "expected_increment"),
    [
        ("NONE", VersionIncrement.NONE),
        ("PATCH", VersionIncrement.PATCH),
        ("MINOR", VersionIncrement.MINOR),
        ("MAJOR", VersionIncrement.MAJOR),
    ],
)
def test_version_increment_from_value_with_valid_strings(value, expected_increment):
    """Test from_value with valid string enum names."""
    assert VersionIncrement.from_value(value) == expected_increment


@pytest.mark.parametrize(
    "invalid_value",
    [
        "INVALID",
        "patch",  # case sensitive
        "",
        "none",
        "major",
    ],
)
def test_version_increment_from_value_with_invalid_string(invalid_value):
    """Test from_value with invalid string returns NONE."""
    assert VersionIncrement.from_value(invalid_value) == VersionIncrement.NONE


@pytest.mark.parametrize(
    "non_string_value",
    [
        0,
        1,
        None,
        [],
        {},
        True,
        False,
    ],
)
def test_version_increment_from_value_with_non_string(non_string_value):
    """Test from_value with non-string values returns NONE."""
    assert VersionIncrement.from_value(non_string_value) == VersionIncrement.NONE


@pytest.mark.parametrize(
    ("smaller", "larger"),
    [
        (VersionIncrement.NONE, VersionIncrement.PATCH),
        (VersionIncrement.PATCH, VersionIncrement.MINOR),
        (VersionIncrement.MINOR, VersionIncrement.MAJOR),
        (VersionIncrement.NONE, VersionIncrement.MAJOR),
    ],
)
def test_version_increment_comparison(smaller, larger):
    """Test that VersionIncrement can be compared as integers."""
    assert smaller < larger
    assert larger > smaller
