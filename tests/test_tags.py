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
