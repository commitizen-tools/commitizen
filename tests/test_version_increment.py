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
        (None, VersionIncrement.NONE),
        (123, VersionIncrement.NONE),
    ],
)
def test_version_increment_from_value(
    value: object, expected: VersionIncrement
) -> None:
    assert VersionIncrement.from_value(value) == expected


def test_version_increment_str() -> None:
    assert str(VersionIncrement.PATCH) == "PATCH"
