import pytest
from freezegun import freeze_time
from packaging.version import Version

from commitizen import bump

conversion = [
    (("1.2.3", "v$version"), "v1.2.3"),
    (("1.2.3a2", "v$version"), "v1.2.3a2"),
    (("1.2.3b2", "v$version"), "v1.2.3b2"),
    (("1.2.3", "ver$major.$minor.$patch"), "ver1.2.3"),
    (("1.2.3a0", "ver$major.$minor.$patch.$prerelease"), "ver1.2.3.a0"),
    (("1.2.3rc2", "$major.$minor.$patch.$prerelease-majestic"), "1.2.3.rc2-majestic"),
    (("1.2.3+1.0.0", "v$version"), "v1.2.3+1.0.0"),
    (("1.2.3+1.0.0", "v$version-local"), "v1.2.3+1.0.0-local"),
    (("1.2.3+1.0.0", "ver$major.$minor.$patch"), "ver1.2.3"),
    (("1.2.3a1", "%y.%m.%d$prerelease"), "21.05.06a1"),
    (("1.2.3a1", "%Y.%-m.%-d$prerelease"), "2021.5.6a1"),
    (("1.2.3a1", "%y.%-m.$major.$minor"), "21.5.1.2"),
    (("2021.01.31a1", "%Y.%-m.%-d$prerelease"), "2021.5.6a1"),
    (("21.04.02", "%y.%m.%d"), "21.05.06"),
    (("21.4.2.1.2", "%y.%-m.%-d.$major.$minor"), "21.5.6.1.2"),
]


@freeze_time("2021-5-6")
@pytest.mark.parametrize("test_input,expected", conversion)
def test_create_tag(test_input, expected):
    version, format = test_input
    new_tag = bump.create_tag(Version(version), format)
    assert new_tag == expected
