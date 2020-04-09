"""
CC: Conventional commits
SVE: Semantic version at the end
"""
from collections import OrderedDict

import pytest

from commitizen import bump, defaults
from commitizen.git import GitCommit

NONE_INCREMENT_CC = ["docs(README): motivation", "ci: added travis"]

PATCH_INCREMENTS_CC = [
    "fix(setup.py): future is now required for every python version",
    "docs(README): motivation",
]

MINOR_INCREMENTS_CC = [
    "feat(cli): added version",
    "docs(README): motivation",
    "fix(setup.py): future is now required for every python version",
]

MAJOR_INCREMENTS_CC = [
    "feat(cli): added version",
    "docs(README): motivation",
    "BREAKING CHANGE: `extends` key in config file is now used for extending other config files",  # noqa
    "fix(setup.py): future is now required for every python version",
]

BUMP_PATTERN_REGEX_CC = r"^(BREAKING[\-\ ]CHANGE|feat|fix|refactor|perf)(\(.+\))?(!)?"
BUMP_MAP_REGEX_CC = OrderedDict(
    (
        (r"^.+!$", defaults.MAJOR),
        (r"^BREAKING[\-\ ]CHANGE", defaults.MAJOR),
        (r"^feat", defaults.MINOR),
        (r"^fix", defaults.PATCH),
        (r"^refactor", defaults.PATCH),
        (r"^perf", defaults.PATCH),
    )
)
MAJOR_INCREMENTS_REGEX_CC = [
    "feat(cli)!: added version",
    "BREAKING CHANGE: break everything",
    "BREAKING-CHANGE: alternative breaking change key",
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
    "messages, expected_type, regex, increment_map",
    (
        (PATCH_INCREMENTS_CC, "PATCH", defaults.bump_pattern, defaults.bump_map),
        (MINOR_INCREMENTS_CC, "MINOR", defaults.bump_pattern, defaults.bump_map),
        (MAJOR_INCREMENTS_CC, "MAJOR", defaults.bump_pattern, defaults.bump_map),
        (MAJOR_INCREMENTS_REGEX_CC, "MAJOR", BUMP_PATTERN_REGEX_CC, BUMP_MAP_REGEX_CC),
        (NONE_INCREMENT_CC, None, defaults.bump_pattern, defaults.bump_map),
    ),
)
def test_find_increment(messages, expected_type, regex, increment_map):
    commits = [GitCommit(rev="test", title=message) for message in messages]
    increment_type = bump.find_increment(commits, regex, increment_map)
    assert increment_type == expected_type


@pytest.mark.parametrize(
    "messages, expected_type",
    (
        (PATCH_INCREMENTS_SVE, "PATCH"),
        (MINOR_INCREMENTS_SVE, "MINOR"),
        (MAJOR_INCREMENTS_SVE, "MAJOR"),
    ),
)
def test_find_increment_sve(messages, expected_type):
    commits = [GitCommit(rev="test", title=message) for message in messages]
    increment_type = bump.find_increment(
        commits, regex=semantic_version_pattern, increments_map=semantic_version_map
    )
    assert increment_type == expected_type
