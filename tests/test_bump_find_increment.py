"""
CC: Conventional commits
SVE: Semantic version at the end
"""
from commitizen import bump


PATCH_INCREMENTS_CC = [
    "docs(README): motivation",
    "fix(setup.py): future is now required for every python version",
]

MINOR_INCREMENTS_CC = [
    "feat(cli): added version",
    "docs(README): motivation",
    "fix(setup.py): future is now required for every python version",
]

MAJOR_INCREMENTS_CC = [
    "feat(cli): added version",
    "docs(README): motivation",
    "fix(setup.py): future is now required for every python version",
    "BREAKING CHANGE: `extends` key in config file is now used for extending other config files",
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


def test_find_increment_type_patch():
    messages = PATCH_INCREMENTS_CC
    increment_type = bump.find_increment(messages)
    assert increment_type == "PATCH"


def test_find_increment_type_minor():
    messages = MINOR_INCREMENTS_CC
    increment_type = bump.find_increment(messages)
    assert increment_type == "MINOR"


def test_find_increment_type_major():
    messages = MAJOR_INCREMENTS_CC
    increment_type = bump.find_increment(messages)
    assert increment_type == "MAJOR"


def test_find_increment_type_patch_sve():
    messages = PATCH_INCREMENTS_SVE
    increment_type = bump.find_increment(
        messages, regex=semantic_version_pattern, increments_map=semantic_version_map
    )
    assert increment_type == "PATCH"


def test_find_increment_type_minor_sve():
    messages = MINOR_INCREMENTS_SVE
    increment_type = bump.find_increment(
        messages, regex=semantic_version_pattern, increments_map=semantic_version_map
    )
    assert increment_type == "MINOR"


def test_find_increment_type_major_sve():
    messages = MAJOR_INCREMENTS_SVE
    increment_type = bump.find_increment(
        messages, regex=semantic_version_pattern, increments_map=semantic_version_map
    )
    assert increment_type == "MAJOR"
