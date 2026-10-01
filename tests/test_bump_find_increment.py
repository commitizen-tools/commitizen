"""Regression tests for the public ``commitizen.bump.find_increment`` helper."""

from commitizen import bump
from commitizen.cz.conventional_commits import ConventionalCommitsCz
from commitizen.git import GitCommit


def test_find_increment_keeps_public_api_behavior() -> None:
    """The compatibility shim still returns the highest named increment."""
    # Arrange
    commits = [
        GitCommit(rev="test", title="fix: correct typo"),
        GitCommit(rev="test", title="feat(api): add endpoint"),
    ]

    # Act
    increment = bump.find_increment(
        commits,
        regex=ConventionalCommitsCz.bump_pattern,
        increments_map=ConventionalCommitsCz.bump_map,
    )

    # Assert
    assert increment == "MINOR"


def test_find_increment_supports_custom_none_mapping() -> None:
    """A matched custom rule can still opt out of bumping entirely."""
    # Arrange
    commits = [GitCommit(rev="test", title="docs: expand usage guide")]

    # Act
    increment = bump.find_increment(
        commits,
        regex=r"^(docs)",
        increments_map={"docs": None},
    )

    # Assert
    assert increment is None
