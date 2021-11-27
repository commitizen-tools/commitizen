from collections import OrderedDict
from typing import Any, List, Optional, Tuple, TypedDict


# Type
class Settings(TypedDict, total=False):
    name: str
    version: Optional[str]
    version_files: List[str]
    tag_format: Optional[str]
    bump_message: Optional[str]
    changelog_file: str
    changelog_incremental: bool
    changelog_start_rev: Optional[str]
    update_changelog_on_bump: bool
    use_shortcuts: bool
    style: Optional[List[Tuple[str, str]]]
    customize: Any


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
bump_message = "bump: version $current_version → $new_version"

change_type_order = ["BREAKING CHANGE", "feat", "fix", "refactor", "perf"]

commit_parser = r"^(?P<change_type>feat|fix|refactor|perf|BREAKING CHANGE)(?:\((?P<scope>[^()\r\n]*)\)|\()?(?P<breaking>!)?:\s(?P<message>.*)?"  # noqa
version_parser = r"(?P<version>([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+)?(\w+)?)"
