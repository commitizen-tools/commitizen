from commitizen.git import GitTag
from commitizen.tags import TagRules


def _git_tag(name: str) -> GitTag:
    return GitTag(name, "rev", "2024-01-01")


def test_find_tag_for_partial_version_returns_latest_match():
    tags = [
        _git_tag("1.2.0"),
        _git_tag("1.2.2"),
        _git_tag("1.2.1"),
        _git_tag("1.3.0"),
    ]

    rules = TagRules()

    found = rules.find_tag_for(tags, "1.2")

    assert found is not None
    assert found.name == "1.2.2"


def test_find_tag_for_full_version_remains_exact():
    tags = [
        _git_tag("1.2.0"),
        _git_tag("1.2.2"),
        _git_tag("1.2.1"),
    ]

    rules = TagRules()

    found = rules.find_tag_for(tags, "1.2.1")

    assert found is not None
    assert found.name == "1.2.1"


def test_find_tag_for_partial_version_with_prereleases_prefers_latest_version():
    tags = [
        _git_tag("1.2.0b1"),
        _git_tag("1.2.0"),
        _git_tag("1.2.1b1"),
    ]

    rules = TagRules()

    found = rules.find_tag_for(tags, "1.2")

    assert found is not None
    # 1.2.1b1 > 1.2.0 so it should be selected
    assert found.name == "1.2.1b1"


def test_find_tag_for_partial_version_respects_tag_format():
    tags = [
        _git_tag("v1.2.0"),
        _git_tag("v1.2.1"),
        _git_tag("v1.3.0"),
    ]

    rules = TagRules(tag_format="v$version")

    found = rules.find_tag_for(tags, "1.2")

    assert found is not None
    assert found.name == "v1.2.1"

    found = rules.find_tag_for(tags, "1")

    assert found is not None
    assert found.name == "v1.3.0"


def test_find_tag_for_partial_version_returns_none_when_no_match():
    tags = [
        _git_tag("2.0.0"),
        _git_tag("2.1.0"),
    ]

    rules = TagRules()

    found = rules.find_tag_for(tags, "1.2")

    assert found is None


def test_find_tag_for_partial_version_ignores_invalid_tags():
    tags = [
        _git_tag("not-a-version"),
        _git_tag("1.2.0"),
        _git_tag("1.2.1"),
    ]

    rules = TagRules()

    found = rules.find_tag_for(tags, "1.2")

    assert found is not None
    assert found.name == "1.2.1"


def test_is_version_tag_accepts_semver2_prerelease_in_custom_tag_format():
    """Regression test for #1614: a SemVer2-style prerelease segment such as
    ``rc.0`` (with a literal dot) must be recognised when it appears at the
    position of ``${prerelease}`` in a custom ``tag_format``. Before the
    prerelease regex was widened from ``\\w+\\d+`` to ``\\w+(?:\\.\\w+)*``,
    the tag commitizen itself just created emitted "Invalid version tag"
    warnings on the next changelog/bump.
    """
    from commitizen.version_schemes import get_version_scheme

    scheme = get_version_scheme({"version_scheme": "semver2"})
    rules = TagRules(
        scheme=scheme,
        tag_format="${major}.${minor}-${patch}${prerelease}",
    )

    assert rules.is_version_tag("0.0-2rc.0") is True
    # Plain releases (no prerelease) are still accepted.
    assert rules.is_version_tag("0.0-2") is True
    # Multi-segment SemVer2 prereleases too.
    assert rules.is_version_tag("0.0-2alpha.beta.1") is True

    # And ``extract_version`` round-trips the prerelease portion.
    extracted = rules.extract_version(_git_tag("0.0-2rc.0"))
    assert str(extracted) == "0.0.2-rc.0"


def test_is_version_tag_accepts_dotless_devrelease_in_custom_tag_format():
    """Regression test for #1614: ``${devrelease}`` accepts both ``dev1``
    and ``.dev1`` suffixes when a custom ``tag_format`` splits release and dev
    portions explicitly.
    """
    rules = TagRules(tag_format="version-${major}.${minor}.${patch}${devrelease}")

    assert rules.is_version_tag("version-1.2.3.dev1") is True
    assert rules.is_version_tag("version-1.2.3dev1") is True

    extracted = rules.extract_version(_git_tag("version-1.2.3dev1"))
    assert str(extracted) == "1.2.3.dev1"
