import pytest

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


def test_monorepo_ignored_tag_formats_keep_own_tags(capsys: pytest.CaptureFixture):
    """Regression test for the monorepo workflow in
    ``docs/tutorials/monorepo_guidance.md``.

    Each component configures a suffixed ``tag_format`` and ignores sibling
    component tags with a wildcard.

    Ignoring sibling tags must not reject the component's own tags. Ignored
    tags are expected noise, so they must not emit "Invalid version tag"
    warnings; only truly unexpected tags warn.
    """
    library_foo_rules = TagRules(
        tag_format="${version}-library-foo",
        ignored_tag_formats=["${version}-library-(?!foo$).*"],
    )
    library_zoo_rules = TagRules(
        tag_format="${version}-library-zoo",
        ignored_tag_formats=["${version}-library-(?!zoo$).*"],
    )

    # Own tags remain version tags, sibling tags are filtered out.
    assert library_foo_rules.is_version_tag("1.0.0-library-foo") is True
    assert library_foo_rules.is_version_tag("1.0.0-library-zoo") is False

    assert library_zoo_rules.is_version_tag("1.0.0-library-zoo") is True
    assert library_zoo_rules.is_version_tag("1.0.0-library-foo") is False

    # Check also for prefix
    assert library_foo_rules.is_ignored_tag("1.0.0-library-foobar") is True

    # The own tag is parseable, so a rejection above is a filtering problem,
    # not a parsing one.
    extracted = library_foo_rules.extract_version(_git_tag("1.0.0-library-foo"))
    assert str(extracted) == "1.0.0"

    # Ignored tags do not warn. Unknown tags still do.
    library_foo_rules.is_version_tag("1.0.0-library-zoo", warn=True)
    library_foo_rules.is_version_tag("unexpected-tag", warn=True)
    captured = capsys.readouterr()
    assert "1.0.0-library-zoo" not in captured.err
    assert "unexpected-tag" in captured.err


def test_monorepo_get_version_tags_filters_sibling_components(
    capsys: pytest.CaptureFixture,
):
    """``get_version_tags`` keeps only the component's own tags when the
    repository also contains sibling component tags, as configured in
    ``docs/tutorials/monorepo_guidance.md``.

    The changelog and the ``scm`` version provider use this filtering, so the
    ignored wildcard must silence sibling tags without dropping this
    component's own tags.
    """
    tags = [
        _git_tag("1.0.0-library-b"),
        _git_tag("1.0.0-library-z"),
        _git_tag("1.1.0-library-b"),
        _git_tag("unexpected-tag"),
    ]
    rules = TagRules(
        tag_format="${version}-library-b",
        ignored_tag_formats=["${version}-library-(?!b$).*"],
    )

    version_tags = rules.get_version_tags(tags, warn=True)

    assert [t.name for t in version_tags] == [
        "1.0.0-library-b",
        "1.1.0-library-b",
    ]

    # Only the truly unexpected tag warns; sibling tags are known noise.
    captured = capsys.readouterr()
    assert "unexpected-tag" in captured.err
    assert "1.0.0-library-z" not in captured.err
