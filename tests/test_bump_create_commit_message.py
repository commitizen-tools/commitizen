import pytest
from packaging.version import Version

from commitizen import bump

conversion = [
    (
        ("1.2.3", "1.3.0", "bump: $current_version -> $new_version [skip ci]"),
        "bump: 1.2.3 -> 1.3.0 [skip ci]",
    ),
    (("1.2.3", "1.3.0", None), "bump: version 1.2.3 → 1.3.0"),
    (("1.2.3", "1.3.0", "release $new_version"), "release 1.3.0"),
]


@pytest.mark.parametrize("test_input,expected", conversion)
def test_create_tag(test_input, expected):
    current_version, new_version, message_template = test_input
    new_tag = bump.create_commit_message(
        Version(current_version), Version(new_version), message_template
    )
    assert new_tag == expected
