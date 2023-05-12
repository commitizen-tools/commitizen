import re
from typing import Dict

import pytest
from packaging.version import Version

from commitizen.tags import make_tag_pattern, tag_from_version

TAG_FORMATS: Dict[str, Dict[str, list]] = {
    "v$version": {
        "tags_per_version": [
            ("1.2.3", "v1.2.3"),
            ("1.2.3a2", "v1.2.3a2"),
            ("1.2.3b2", "v1.2.3b2"),
            ("1.2.3+1.0.0", "v1.2.3+1.0.0"),
        ],
        "invalid_tags": ["1.2.3", "unknown-tag", "v1-2-3"],
    },
    "ver$major-$minor-$patch$prerelease": {
        "tags_per_version": [
            ("1.2.3", "ver1-2-3"),
            ("1.2.3a0", "ver1-2-3a0"),
            ("1.2.3+1.0.0", "ver1-2-3"),
        ],
        "invalid_tags": ["1.2.3", "unknown-tag", "v1-2-3", "v1.0.0", "ver1.0.0+123"],
    },
    "ver$major.$minor.$patch$prerelease-majestic": {
        "tags_per_version": [
            ("1.2.3rc2", "ver1.2.3rc2-majestic"),
        ],
        "invalid_tags": ["1.2.3", "unknown-tag", "v1-2-3", "v1.0.0", "ver1.0.0"],
    },
    "v$version-local": {
        "tags_per_version": [("1.2.3+1.0.0", "v1.2.3+1.0.0-local")],
        "invalid_tags": ["1.2.3", "unknown-tag", "v1-2-3", "v1.0.0", "ver1.0.0"],
    },
}


@pytest.mark.parametrize(
    "tag_format, version, expected_tag_name",
    [
        (tag_format, version, expected_tag_name)
        for tag_format, format_dict in TAG_FORMATS.items()
        for version, expected_tag_name in format_dict["tags_per_version"]
    ],
)
def test_tag_from_version(tag_format, version, expected_tag_name):
    new_tag = tag_from_version(Version(version), tag_format)
    assert new_tag == expected_tag_name


@pytest.mark.parametrize(
    "tag_format,tag_name",
    [
        (tag_format, tag_name)
        for tag_format, format_dict in TAG_FORMATS.items()
        for _, tag_name in format_dict["tags_per_version"]
    ],
)
def test_make_tag_pattern_matches(tag_format: str, tag_name: str):
    pattern = re.compile(make_tag_pattern(tag_format=tag_format), flags=re.VERBOSE)
    assert pattern.fullmatch(tag_name)


@pytest.mark.parametrize(
    "tag_format,invalid_tag_name",
    [
        (tag_format, invalid_tag_name)
        for tag_format, format_dict in TAG_FORMATS.items()
        for invalid_tag_name in format_dict["invalid_tags"]
    ],
)
def test_make_tag_pattern_does_not_match(tag_format: str, invalid_tag_name: str):
    pattern = re.compile(make_tag_pattern(tag_format=tag_format), flags=re.VERBOSE)
    assert pattern.fullmatch(invalid_tag_name) is None
