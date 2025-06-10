from __future__ import annotations

import pathlib
import warnings
from collections import OrderedDict
from collections.abc import Iterable, MutableMapping, Sequence
from typing import Any, TypedDict

from commitizen.question import CzQuestion


class CzSettings(TypedDict, total=False):
    bump_pattern: str
    bump_map: OrderedDict[str, str]
    bump_map_major_version_zero: OrderedDict[str, str]
    change_type_order: list[str]

    questions: Iterable[CzQuestion]
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
    allow_abort: bool
    allowed_prefixes: list[str]
    always_signoff: bool
    annotated_tag: bool
    bump_message: str | None
    change_type_map: dict[str, str]
    changelog_file: str
    changelog_format: str | None
    changelog_incremental: bool
    changelog_merge_prerelease: bool
    changelog_start_rev: str | None
    customize: CzSettings
    encoding: str
    extras: dict[str, Any]
    gpg_sign: bool
    ignored_tag_formats: Sequence[str]
    legacy_tag_formats: Sequence[str]
    major_version_zero: bool
    name: str
    post_bump_hooks: list[str] | None
    pre_bump_hooks: list[str] | None
    prerelease_offset: int
    retry_after_failure: bool
    style: list[tuple[str, str]]
    tag_format: str
    template: str | None
    update_changelog_on_bump: bool
    use_shortcuts: bool
    version_files: list[str]
    version_provider: str | None
    version_scheme: str | None
    version_type: str | None
    version: str | None


CONFIG_FILES: list[str] = [
    "pyproject.toml",
    ".cz.toml",
    ".cz.json",
    "cz.json",
    ".cz.yaml",
    "cz.yaml",
    "cz.toml",
]
ENCODING = "utf-8"

DEFAULT_SETTINGS: Settings = {
    "name": "cz_conventional_commits",
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
    "encoding": ENCODING,
    "always_signoff": False,
    "template": None,  # default provided by plugin
    "extras": {},
}

MAJOR = "MAJOR"
MINOR = "MINOR"
PATCH = "PATCH"

CHANGELOG_FORMAT = "markdown"

BUMP_PATTERN = r"^((BREAKING[\-\ ]CHANGE|\w+)(\(.+\))?!?):"
BUMP_MAP = OrderedDict(
    (
        (r"^.+!$", MAJOR),
        (r"^BREAKING[\-\ ]CHANGE", MAJOR),
        (r"^feat", MINOR),
        (r"^fix", PATCH),
        (r"^refactor", PATCH),
        (r"^perf", PATCH),
    )
)
BUMP_MAP_MAJOR_VERSION_ZERO = OrderedDict(
    (
        (r"^.+!$", MINOR),
        (r"^BREAKING[\-\ ]CHANGE", MINOR),
        (r"^feat", MINOR),
        (r"^fix", PATCH),
        (r"^refactor", PATCH),
        (r"^perf", PATCH),
    )
)
CHANGE_TYPE_ORDER = ["BREAKING CHANGE", "Feat", "Fix", "Refactor", "Perf"]
BUMP_MESSAGE = "bump: version $current_version → $new_version"


def get_tag_regexes(
    version_regex: str,
) -> dict[str, str]:
    regexes = {
        "version": version_regex,
        "major": r"(?P<major>\d+)",
        "minor": r"(?P<minor>\d+)",
        "patch": r"(?P<patch>\d+)",
        "prerelease": r"(?P<prerelease>\w+\d+)?",
        "devrelease": r"(?P<devrelease>\.dev\d+)?",
    }
    return {
        **{f"${k}": v for k, v in regexes.items()},
        **{f"${{{k}}}": v for k, v in regexes.items()},
    }


# Type
Questions = Iterable[MutableMapping[str, Any]]  # TODO: remove this in v5


def __getattr__(name: str) -> Any:
    # PEP-562: deprecate module-level variable

    # {"deprecated key": (value, "new key")}
    deprecated_vars = {
        "bump_pattern": (BUMP_PATTERN, "BUMP_PATTERN"),
        "bump_map": (BUMP_MAP, "BUMP_MAP"),
        "bump_map_major_version_zero": (
            BUMP_MAP_MAJOR_VERSION_ZERO,
            "BUMP_MAP_MAJOR_VERSION_ZERO",
        ),
        "bump_message": (BUMP_MESSAGE, "BUMP_MESSAGE"),
        "change_type_order": (CHANGE_TYPE_ORDER, "CHANGE_TYPE_ORDER"),
        "encoding": (ENCODING, "ENCODING"),
        "name": (DEFAULT_SETTINGS["name"], "DEFAULT_SETTINGS['name']"),
        "Questions": (Questions, "Iterable[CzQuestion]"),
    }
    if name in deprecated_vars:
        value, replacement = deprecated_vars[name]
        warnings.warn(
            f"{name} is deprecated and will be removed in v5. "
            f"Use {replacement} instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return value
    raise AttributeError(f"{name} is not an attribute of {__name__}")
