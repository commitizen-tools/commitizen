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
