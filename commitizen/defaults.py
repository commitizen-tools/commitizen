from __future__ import annotations

import pathlib
import sys
from collections import OrderedDict
from typing import Any, Iterable, MutableMapping

if sys.version_info < (3, 8):
    from typing_extensions import TypedDict
else:
    from typing import TypedDict

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
    tag_format: str | None
    bump_message: str | None
    allow_abort: bool
    changelog_file: str
    changelog_incremental: bool
    changelog_start_rev: str | None
    changelog_merge_prerelease: bool
    update_changelog_on_bump: bool
    use_shortcuts: bool
    style: list[tuple[str, str]] | None
    customize: CzSettings
    major_version_zero: bool
    pre_bump_hooks: list[str] | None
    post_bump_hooks: list[str] | None
    prerelease_offset: int


name: str = "cz_conventional_commits"
config_files: list[str] = [
    "pyproject.toml",
    ".cz.toml",
    ".cz.json",
    "cz.json",
    ".cz.yaml",
    "cz.yaml",
]

DEFAULT_SETTINGS: Settings = {
    "name": "cz_conventional_commits",
    "version": None,
    "version_files": [],
    "version_provider": "commitizen",
    "version_scheme": None,
    "tag_format": None,  # example v$version
    "bump_message": None,  # bumped v$current_version to $new_version
    "allow_abort": False,
    "changelog_file": "CHANGELOG.md",
    "changelog_incremental": False,
    "changelog_start_rev": None,
    "changelog_merge_prerelease": False,
    "update_changelog_on_bump": False,
    "use_shortcuts": False,
    "major_version_zero": False,
    "pre_bump_hooks": [],
    "post_bump_hooks": [],
    "prerelease_offset": 0,
}

MAJOR = "MAJOR"
MINOR = "MINOR"
PATCH = "PATCH"

bump_pattern = r"^(((BREAKING[\-\ ]CHANGE|feat|fix|refactor|perf)(\(.+\))?(!)?)|\w+!):"
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

commit_parser = r"^((?P<change_type>feat|fix|refactor|perf|BREAKING CHANGE)(?:\((?P<scope>[^()\r\n]*)\)|\()?(?P<breaking>!)?|\w+!):\s(?P<message>.*)?"  # noqa
