import pytest
from packaging.version import Version
from commitizen import bump

conversion = [
    (("1.2.3", "v$version"), "v1.2.3"),
    (("1.2.3a2", "v$version"), "v1.2.3a2"),
    (("1.2.3b2", "v$version"), "v1.2.3b2"),
    (("1.2.3", "ver$major.$minor.$patch"), "ver1.2.3"),
    (("1.2.3a0", "ver$major.$minor.$patch.$prerelease"), "ver1.2.3.a0"),
    (("1.2.3rc2", "$major.$minor.$patch.$prerelease-majestic"), "1.2.3.rc2-majestic"),
]


@pytest.mark.parametrize("test_input,expected", conversion)
def test_create_tag(test_input, expected):
    version, format = test_input
    new_tag = bump.create_tag(Version(version), format)
    assert new_tag == expected
