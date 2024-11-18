from __future__ import annotations

import pathlib
from collections import OrderedDict
from collections.abc import Iterable, MutableMapping, Sequence
from typing import Any, TypedDict

# Type
Questions = Iterable[MutableMapping[str, Any]]


class CzSettings(TypedDict, total=False):
    bump_pattern: str
    bump_map: OrderedDict[str, str]
    bump_map_major_version_zero: OrderedDict[str, str]
    change_type_order: list[str]

    questions: Questions
    example: str | None
    schema_pattern: str | None
    schema: str | None
    info_path: str | pathlib.Path
    info: str
    message_template: str
    commit_parser: str | None
    changelog_pattern: str | None
    change_type_map: dict[str, str] | None


class Settings(TypedDict, total=False):
    name: str
    version: str | None
    version_files: list[str]
    version_provider: str | None
    version_scheme: str | None
    version_type: str | None
    tag_format: str
    legacy_tag_formats: Sequence[str]
    ignored_tag_formats: Sequence[str]
    bump_message: str | None
    retry_after_failure: bool
    allow_abort: bool
    allowed_prefixes: list[str]
    changelog_file: str
    changelog_format: str | None
    changelog_incremental: bool
    changelog_start_rev: str | None
    changelog_merge_prerelease: bool
    update_changelog_on_bump: bool
    use_shortcuts: bool
    style: list[tuple[str, str]]
    customize: CzSettings
    major_version_zero: bool
    pre_bump_hooks: list[str] | None
    post_bump_hooks: list[str] | None
    prerelease_offset: int
    encoding: str
    always_signoff: bool
    template: str | None
    extras: dict[str, Any]


name: str = "cz_conventional_commits"
config_files: list[str] = [
    "pyproject.toml",
    ".cz.toml",
    ".cz.json",
    "cz.json",
    ".cz.yaml",
    "cz.yaml",
    "cz.toml",
]
encoding: str = "utf-8"

DEFAULT_SETTINGS: Settings = {
    "name": name,
    "version": None,
    "version_files": [],
    "version_provider": "commitizen",
    "version_scheme": None,
    "tag_format": "$version",  # example v$version
    "legacy_tag_formats": [],
    "ignored_tag_formats": [],
    "bump_message": None,  # bumped v$current_version to $new_version
    "retry_after_failure": False,
    "allow_abort": False,
    "allowed_prefixes": [
        "Merge",
        "Revert",
        "Pull request",
        "fixup!",
        "squash!",
    ],
    "changelog_file": "CHANGELOG.md",
    "changelog_format": None,  # default guessed from changelog_file
    "changelog_incremental": False,
    "changelog_start_rev": None,
    "changelog_merge_prerelease": False,
    "update_changelog_on_bump": False,
    "use_shortcuts": False,
    "major_version_zero": False,
    "pre_bump_hooks": [],
    "post_bump_hooks": [],
    "prerelease_offset": 0,
    "encoding": encoding,
    "always_signoff": False,
    "template": None,  # default provided by plugin
    "extras": {},
}

MAJOR = "MAJOR"
MINOR = "MINOR"
PATCH = "PATCH"

CHANGELOG_FORMAT = "markdown"

bump_pattern = r"^((BREAKING[\-\ ]CHANGE|\w+)(\(.+\))?!?):"
bump_map = OrderedDict(
    (
        (r"^.+!$", MAJOR),
        (r"^BREAKING[\-\ ]CHANGE", MAJOR),
        (r"^feat", MINOR),
        (r"^fix", PATCH),
        (r"^refactor", PATCH),
        (r"^perf", PATCH),
    )
)
bump_map_major_version_zero = OrderedDict(
    (
        (r"^.+!$", MINOR),
        (r"^BREAKING[\-\ ]CHANGE", MINOR),
        (r"^feat", MINOR),
        (r"^fix", PATCH),
        (r"^refactor", PATCH),
        (r"^perf", PATCH),
    )
)
change_type_order = ["BREAKING CHANGE", "Feat", "Fix", "Refactor", "Perf"]
bump_message = "bump: version $current_version → $new_version"


def get_tag_regexes(
    version_regex: str,
) -> dict[str, str]:
    regexs = {
        "version": version_regex,
        "major": r"(?P<major>\d+)",
        "minor": r"(?P<minor>\d+)",
        "patch": r"(?P<patch>\d+)",
        "prerelease": r"(?P<prerelease>\w+\d+)?",
        "devrelease": r"(?P<devrelease>\.dev\d+)?",
    }
    return {
        **{f"${k}": v for k, v in regexs.items()},
        **{f"${{{k}}}": v for k, v in regexs.items()},
    }
