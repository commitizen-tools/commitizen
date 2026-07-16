import pytest

from commitizen.version_increment import VersionIncrement


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("MAJOR", VersionIncrement.MAJOR),
        ("MINOR", VersionIncrement.MINOR),
        ("PATCH", VersionIncrement.PATCH),
        ("NONE", VersionIncrement.NONE),
        ("not_a_valid_name", VersionIncrement.NONE),
        ("major", VersionIncrement.NONE),  # case sensitive
        ("", VersionIncrement.NONE),
        (None, VersionIncrement.NONE),
        (123, VersionIncrement.NONE),
        (True, VersionIncrement.NONE),
        ([], VersionIncrement.NONE),
        ({}, VersionIncrement.NONE),
        (VersionIncrement.MAJOR, VersionIncrement.NONE),  # enum value itself
    ],
)
def test_version_increment_from_value(
    value: object, expected: VersionIncrement
) -> None:
    assert VersionIncrement.from_value(value) == expected
    # ``safe_cast`` is an alias used by the BumpRule plumbing.
    assert VersionIncrement.safe_cast(value) == expected


def test_version_increment_str() -> None:
    assert str(VersionIncrement.PATCH) == "PATCH"
