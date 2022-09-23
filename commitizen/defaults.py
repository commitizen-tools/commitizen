import pathlib
from collections import OrderedDict
from typing import Any, Dict, Iterable, List, MutableMapping, Optional, Tuple, Union

from typing_extensions import TypedDict

# Type
Questions = Iterable[MutableMapping[str, Any]]


class CzSettings(TypedDict, total=False):
    bump_pattern: str
    bump_map: "OrderedDict[str, str]"
    change_type_order: List[str]

    questions: Questions
    example: Optional[str]
    schema_pattern: Optional[str]
    schema: Optional[str]
    info_path: Union[str, pathlib.Path]
    info: str
    message_template: str
    commit_parser: Optional[str]
    changelog_pattern: Optional[str]
    change_type_map: Optional[Dict[str, str]]


class Settings(TypedDict, total=False):
    name: str
    version: Optional[str]
    version_files: List[str]
    tag_format: Optional[str]
    bump_message: Optional[str]
    bump_pattern: Optional[str]
    bump_map: Optional[Dict[str, str]]
    allow_abort: bool
    changelog_file: str
    changelog_incremental: bool
    changelog_start_rev: Optional[str]
    changelog_pattern: Optional[str]
    update_changelog_on_bump: bool
    use_shortcuts: bool
    style: List[Tuple[str, str]]
    customize: CzSettings
    change_type_order: Optional[List[str]]
    change_type_map: Optional[Dict[str, str]]
    commit_parser: Optional[str]
    schema: str
    schema_pattern: str
    questions: Questions


name: str = "cz_conventional_commits"
config_files: List[str] = [
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
    "tag_format": None,  # example v$version
    "bump_message": None,  # bumped v$current_version to $new_version
    "allow_abort": False,
    "changelog_file": "CHANGELOG.md",
    "changelog_incremental": False,
    "changelog_start_rev": None,
    "update_changelog_on_bump": False,
    "use_shortcuts": False,
}

MAJOR = "MAJOR"
MINOR = "MINOR"
PATCH = "PATCH"

bump_pattern = r"^(BREAKING[\-\ ]CHANGE|feat|fix|refactor|perf)(\(.+\))?(!)?"
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
change_type_order: Optional[List[str]] = None

bump_message = "bump: version $current_version → $new_version"

commit_parser = r"^(?P<change_type>feat|fix|refactor|perf|BREAKING CHANGE)(?:\((?P<scope>[^()\r\n]*)\)|\()?(?P<breaking>!)?:\s(?P<message>.*)?"  # noqa
version_parser = r"(?P<version>([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+)?(\w+)?)"

change_type_map = {
    "feat": "Feat",
    "fix": "Fix",
    "refactor": "Refactor",
    "perf": "Perf",
}

changelog_pattern = bump_pattern

style: List[Tuple[str, str]] = [
    ("qmark", "fg:#ff9d00 bold"),
    ("question", "bold"),
    ("answer", "fg:#ff9d00 bold"),
    ("pointer", "fg:#ff9d00 bold"),
    ("highlighted", "fg:#ff9d00 bold"),
    ("selected", "fg:#cc5454"),
    ("separator", "fg:#cc5454"),
    ("instruction", ""),
    ("text", ""),
    ("disabled", "fg:#858585 italic"),
]
