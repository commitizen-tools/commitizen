import os

import pytest

from commitizen import changelog

CHANGELOG_A = """
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Start using "changelog" over "change log" since it's the common usage.

## [1.0.0] - 2017-06-20
### Added
- New visual identity by [@tylerfortune8](https://github.com/tylerfortune8).
- Version navigation.
""".strip()

CHANGELOG_B = """
## [Unreleased]
- Start using "changelog" over "change log" since it's the common usage.

## 1.2.0
""".strip()

CHANGELOG_C = """
# Unreleased

## v1.0.0
"""

CHANGELOG_D = """
## Unreleased
- Start using "changelog" over "change log" since it's the common usage.
"""


@pytest.fixture
def changelog_a_file():
    changelog_path = "tests/CHANGELOG.md"

    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(CHANGELOG_A)

    yield changelog_path

    os.remove(changelog_path)


@pytest.fixture
def changelog_b_file():
    changelog_path = "tests/CHANGELOG.md"

    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(CHANGELOG_B)

    yield changelog_path

    os.remove(changelog_path)


@pytest.fixture
def changelog_c_file():
    changelog_path = "tests/CHANGELOG.md"

    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(CHANGELOG_C)

    yield changelog_path

    os.remove(changelog_path)


@pytest.fixture
def changelog_d_file():
    changelog_path = "tests/CHANGELOG.md"

    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(CHANGELOG_D)

    yield changelog_path

    os.remove(changelog_path)


VERSIONS_EXAMPLES = [
    ("## [1.0.0] - 2017-06-20", "1.0.0"),
    (
        "# [10.0.0-next.3](https://github.com/angular/angular/compare/10.0.0-next.2...10.0.0-next.3) (2020-04-22)",
        "10.0.0-next.3",
    ),
    ("### 0.19.1 (Jan 7, 2020)", "0.19.1"),
    ("## 1.0.0", "1.0.0"),
    ("## v1.0.0", "1.0.0"),
    ("## v1.0.0 - (2012-24-32)", "1.0.0"),
    ("# version 2020.03.24", "2020.03.24"),
    ("## [Unreleased]", None),
    ("All notable changes to this project will be documented in this file.", None),
    ("# Changelog", None),
    ("### Bug Fixes", None),
]


@pytest.mark.parametrize("line_from_changelog,output_version", VERSIONS_EXAMPLES)
def test_changelog_detect_version(line_from_changelog, output_version):
    version = changelog.parse_version_from_markdown(line_from_changelog)
    assert version == output_version


TITLES_EXAMPLES = [
    ("## [1.0.0] - 2017-06-20", "##"),
    ("## [Unreleased]", "##"),
    ("# Unreleased", "#"),
]


@pytest.mark.parametrize("line_from_changelog,output_title", TITLES_EXAMPLES)
def test_parse_title_type_of_line(line_from_changelog, output_title):
    title = changelog.parse_title_type_of_line(line_from_changelog)
    assert title == output_title


def test_get_metadata_from_a(changelog_a_file):
    meta = changelog.get_metadata(changelog_a_file, "utf-8")
    assert meta == {
        "latest_version": "1.0.0",
        "latest_version_position": 10,
        "unreleased_end": 10,
        "unreleased_start": 7,
    }


def test_get_metadata_from_b(changelog_b_file):
    meta = changelog.get_metadata(changelog_b_file, "utf-8")
    assert meta == {
        "latest_version": "1.2.0",
        "latest_version_position": 3,
        "unreleased_end": 3,
        "unreleased_start": 0,
    }


def test_get_metadata_from_c(changelog_c_file):
    meta = changelog.get_metadata(changelog_c_file, "utf-8")
    assert meta == {
        "latest_version": "1.0.0",
        "latest_version_position": 3,
        "unreleased_end": 3,
        "unreleased_start": 1,
    }


def test_get_metadata_from_d(changelog_d_file):
    meta = changelog.get_metadata(changelog_d_file, "utf-8")
    assert meta == {
        "latest_version": None,
        "latest_version_position": None,
        "unreleased_end": 2,
        "unreleased_start": 1,
    }
