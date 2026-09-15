"""
CC: Conventional commits
SVE: Semantic version at the end
"""

import pytest

from commitizen import bump
from commitizen.cz.conventional_commits import ConventionalCommitsCz
from commitizen.git import GitCommit

NONE_INCREMENT_CC = [
    "docs(README): motivation",
    "ci: added travis",
    "performance. Remove or disable the reimplemented linters",
    "refactor that how this line starts",
]

PATCH_INCREMENTS_CC = [
    "fix(setup.py): future is now required for every python version",
    "docs(README): motivation",
]

MINOR_INCREMENTS_CC = [
    "feat(cli): added version",
    "docs(README): motivation",
    "fix(setup.py): future is now required for every python version",
    "perf: app is much faster",
    "refactor: app is much faster",
]

MAJOR_INCREMENTS_BREAKING_CHANGE_CC = [
    "feat(cli): added version",
    "docs(README): motivation",
    "BREAKING CHANGE: `extends` key in config file is now used for extending other config files",
    "fix(setup.py): future is now required for every python version",
]

MAJOR_INCREMENTS_BREAKING_CHANGE_ALT_CC = [
    "feat(cli): added version",
    "docs(README): motivation",
    "BREAKING-CHANGE: `extends` key in config file is now used for extending other config files",
    "fix(setup.py): future is now required for every python version",
]

MAJOR_INCREMENTS_EXCLAMATION_CC = [
    "feat(cli)!: added version",
    "docs(README): motivation",
    "fix(setup.py): future is now required for every python version",
]

MAJOR_INCREMENTS_EXCLAMATION_CC_SAMPLE_2 = [
    "feat(pipeline)!: some text with breaking change"
]

MAJOR_INCREMENTS_EXCLAMATION_OTHER_TYPE_CC = [
    "chore!: drop support for Python 3.9",
    "docs(README): motivation",
    "fix(setup.py): future is now required for every python version",
]

MAJOR_INCREMENTS_EXCLAMATION_OTHER_TYPE_WITH_SCOPE_CC = [
    "chore(deps)!: drop support for Python 3.9",
    "docs(README): motivation",
    "fix(setup.py): future is now required for every python version",
]

PATCH_INCREMENTS_SVE = ["readme motivation PATCH", "fix setup.py PATCH"]

MINOR_INCREMENTS_SVE = [
    "readme motivation PATCH",
    "fix setup.py PATCH",
    "added version to cli MINOR",
]

MAJOR_INCREMENTS_SVE = [
    "readme motivation PATCH",
    "fix setup.py PATCH",
    "added version to cli MINOR",
    "extends key is used for other config files MAJOR",
]

semantic_version_pattern = r"(MAJOR|MINOR|PATCH)"
semantic_version_map = {"MAJOR": "MAJOR", "MINOR": "MINOR", "PATCH": "PATCH"}


@pytest.mark.parametrize(
    ("messages", "expected_type"),
    [
        (PATCH_INCREMENTS_CC, "PATCH"),
        (MINOR_INCREMENTS_CC, "MINOR"),
        (MAJOR_INCREMENTS_BREAKING_CHANGE_CC, "MAJOR"),
        (MAJOR_INCREMENTS_BREAKING_CHANGE_ALT_CC, "MAJOR"),
        (MAJOR_INCREMENTS_EXCLAMATION_OTHER_TYPE_CC, "MAJOR"),
        (MAJOR_INCREMENTS_EXCLAMATION_OTHER_TYPE_WITH_SCOPE_CC, "MAJOR"),
        (MAJOR_INCREMENTS_EXCLAMATION_CC, "MAJOR"),
        (MAJOR_INCREMENTS_EXCLAMATION_CC_SAMPLE_2, "MAJOR"),
        (NONE_INCREMENT_CC, None),
    ],
)
def test_find_increment(messages, expected_type):
    commits = [GitCommit(rev="test", title=message) for message in messages]
    increment_type = bump.find_increment(
        commits,
        regex=ConventionalCommitsCz.bump_pattern,
        increments_map=ConventionalCommitsCz.bump_map,
    )
    assert increment_type == expected_type


@pytest.mark.parametrize(
    ("messages", "expected_type"),
    [
        (PATCH_INCREMENTS_SVE, "PATCH"),
        (MINOR_INCREMENTS_SVE, "MINOR"),
        (MAJOR_INCREMENTS_SVE, "MAJOR"),
    ],
)
def test_find_increment_sve(messages, expected_type):
    commits = [GitCommit(rev="test", title=message) for message in messages]
    increment_type = bump.find_increment(
        commits, regex=semantic_version_pattern, increments_map=semantic_version_map
    )
    assert increment_type == expected_type


# Mimics the dependabot pull request body that triggered #1772: a ``ci:``
# title with a commit body that quotes upstream changelog lines, including
# ``fix: ...`` text. None of the body lines should bump the version.
DEPENDABOT_BODY = (
    "Bumps actions/upload-artifact from 5 to 6.\n"
    "<details>\n"
    "<summary>Commits</summary>\n"
    "<ul>\n"
    '<li><a href="...">b5b1a91</a>\n'
    "fix: update <code>@actions/artifact</code> to ^5.0.0 for Node.js 24\n"
    "punycode fix</li>\n"
    '<li><a href="...">5f643d3</a>\n'
    "chore: update license files</li>\n"
    "</ul>\n"
    "</details>\n"
)


def test_find_increment_ignores_type_tokens_in_commit_body():
    """Regression test for #1772: a ``ci:`` commit whose body lists upstream
    commit messages -- including ones that look like ``fix:`` -- must not
    trigger a PATCH bump. Only the title's commit type counts."""
    commit = GitCommit(rev="test", title="ci: bump dep", body=DEPENDABOT_BODY)
    increment_type = bump.find_increment(
        [commit],
        regex=ConventionalCommitsCz.bump_pattern,
        increments_map=ConventionalCommitsCz.bump_map,
    )
    assert increment_type is None


def test_find_increment_still_honors_breaking_change_in_body():
    """The ``BREAKING CHANGE:`` / ``BREAKING-CHANGE:`` footer in a commit body
    must still trigger a MAJOR bump even after the #1772 fix; only commit
    *types* are now restricted to the title."""
    commit = GitCommit(
        rev="test",
        title="feat: new user interface",
        body="some body content\n\nBREAKING CHANGE: age is no longer supported",
    )
    increment_type = bump.find_increment(
        [commit],
        regex=ConventionalCommitsCz.bump_pattern,
        increments_map=ConventionalCommitsCz.bump_map,
    )
    assert increment_type == "MAJOR"
