import pytest

from commitizen.tags import TagRules

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
    # `${devrelease}` substitution (#1615): rendered as `dev<N>` when the
    # version has a dev release, and as the empty string otherwise.
    (("1.2.3.dev1", "v$major.$minor.$patch.$devrelease"), "v1.2.3.dev1"),
    (("1.2.3.dev0", "$major.$minor.$patch$devrelease"), "1.2.3dev0"),
    (("1.2.3", "$major.$minor.$patch$devrelease"), "1.2.3"),
]


@pytest.mark.parametrize(("test_input", "expected"), conversion)
def test_create_tag(test_input, expected):
    version, format = test_input
    rules = TagRules()
    new_tag = rules.normalize_tag(version, format)
    assert new_tag == expected
