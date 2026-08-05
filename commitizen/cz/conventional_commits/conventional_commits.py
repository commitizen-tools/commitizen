from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

from commitizen import defaults
from commitizen.cz.base import BaseCommitizen
from commitizen.cz.utils import multiple_line_breaker, required_validator
from commitizen.question import Choice

if TYPE_CHECKING:
    from commitizen.config import BaseConfig
    from commitizen.question import CzQuestion

__all__ = ["ConventionalCommitsCz"]


def _parse_scope(text: str) -> str:
    return "-".join(text.strip().split())


def _parse_subject(text: str) -> str:
    return required_validator(text.strip(".").strip(), msg="Subject is required.")


class ConventionalCommitsAnswers(TypedDict):
    prefix: str
    scope: str
    subject: str
    body: str
    footer: str
    is_breaking_change: bool


class ConventionalCommitsCz(BaseCommitizen):
    bump_pattern = defaults.BUMP_PATTERN
    bump_map = defaults.BUMP_MAP
    bump_map_major_version_zero = defaults.BUMP_MAP_MAJOR_VERSION_ZERO
    commit_parser = r"^((?P<change_type>feat|fix|refactor|perf|BREAKING CHANGE)(?:\((?P<scope>[^()\r\n]*)\)|\()?(?P<breaking>!)?|\w+!):\s(?P<message>.*)?"
    change_type_map = {
        "feat": "Feat",
        "fix": "Fix",
        "refactor": "Refactor",
        "perf": "Perf",
    }
    change_type_choices = [
        Choice(
            value="fix",
            name=("fix: A bug fix. Correlates with PATCH in SemVer"),
            key="x",
        ),
        Choice(
            value="feat",
            name="feat: A new feature. Correlates with MINOR in SemVer",
            key="f",
        ),
        Choice(
            value="docs",
            name="docs: Documentation only changes",
            key="d",
        ),
        Choice(
            value="style",
            name=(
                "style: Changes that do not affect the "
                "meaning of the code (white-space, formatting,"
                " missing semi-colons, etc)"
            ),
            key="s",
        ),
        Choice(
            value="refactor",
            name=(
                "refactor: A code change that neither fixes a bug nor adds a feature"
            ),
            key="r",
        ),
        Choice(
            value="perf",
            name="perf: A code change that improves performance",
            key="p",
        ),
        Choice(
            value="test",
            name="test: Adding missing or correcting existing tests",
            key="t",
        ),
        Choice(
            value="build",
            name=(
                "build: Changes that affect the build system or "
                "external dependencies (example scopes: pip, docker, npm)"
            ),
            key="b",
        ),
        Choice(
            value="ci",
            name=(
                "ci: Changes to CI configuration files and "
                "scripts (example scopes: GitLabCI)"
            ),
            key="c",
        ),
    ]

    changelog_pattern = defaults.BUMP_PATTERN

    def __init__(self, config: BaseConfig) -> None:
        super().__init__(config)
        self._isolate_mutable_defaults()

        if override_settings := self.config.settings.get("override"):
            self._apply_override_settings(override_settings)
        elif extend_settings := self.config.settings.get("extend"):
            self._apply_extend_settings(extend_settings)

    def _isolate_mutable_defaults(self) -> None:
        # Keep mutable class defaults isolated per instance.
        self.bump_map = OrderedDict(self.bump_map)
        self.bump_map_major_version_zero = OrderedDict(self.bump_map_major_version_zero)
        self.change_type_map = dict(self.change_type_map)
        self.change_type_choices = [*self.change_type_choices]

    def _apply_override_settings(self, settings: defaults.CzOverrideSettings) -> None:
        if bump_pattern := settings.get("bump_pattern"):
            self.bump_pattern = bump_pattern
        if bump_map := settings.get("bump_map"):
            self.bump_map = OrderedDict(bump_map)
        if bump_map_major_version_zero := settings.get("bump_map_major_version_zero"):
            self.bump_map_major_version_zero = OrderedDict(bump_map_major_version_zero)
        if commit_parser := settings.get("commit_parser"):
            self.commit_parser = commit_parser
        if changelog_pattern := settings.get("changelog_pattern"):
            self.changelog_pattern = changelog_pattern
        if change_type_map := settings.get("change_type_map"):
            self.change_type_map = dict(change_type_map)
        if change_type_choices := settings.get("change_type_choices"):
            self.change_type_choices = [*change_type_choices]

    def _apply_extend_settings(self, settings: defaults.CzExtendSettings) -> None:
        if bump_pattern := settings.get("bump_pattern"):
            self.bump_pattern = bump_pattern
        if bump_map := settings.get("bump_map"):
            self.bump_map.update(bump_map)
        if bump_map_major_version_zero := settings.get("bump_map_major_version_zero"):
            self.bump_map_major_version_zero.update(bump_map_major_version_zero)
        if commit_parser := settings.get("commit_parser"):
            self.commit_parser = commit_parser
        if changelog_pattern := settings.get("changelog_pattern"):
            self.changelog_pattern = changelog_pattern
        if change_type_map := settings.get("change_type_map"):
            self.change_type_map.update(change_type_map)
        if change_type_choices := settings.get("change_type_choices"):
            self.change_type_choices.extend(change_type_choices)

    def questions(self) -> list[CzQuestion]:
        return [
            {
                "type": "list",
                "name": "prefix",
                "message": "Select the type of change you are committing",
                "choices": self.change_type_choices,
            },
            {
                "type": "input",
                "name": "scope",
                "message": (
                    "What is the scope of this change? (class or file name): (press [enter] to skip)\n"
                ),
                "filter": _parse_scope,
            },
            {
                "type": "input",
                "name": "subject",
                "filter": _parse_subject,
                "message": (
                    "Write a short and imperative summary of the code changes: (lower case and no period)\n"
                ),
            },
            {
                "type": "input",
                "name": "body",
                "message": (
                    "Provide additional contextual information about the code changes: (press [enter] to skip)\n"
                ),
                "filter": multiple_line_breaker,
            },
            {
                "type": "confirm",
                "name": "is_breaking_change",
                "message": "Is this a BREAKING CHANGE? Correlates with MAJOR in SemVer",
                "default": False,
            },
            {
                "type": "input",
                "name": "footer",
                "message": (
                    "Footer. Information about Breaking Changes and "
                    "reference issues that this commit closes: (press [enter] to skip)\n"
                ),
            },
        ]

    def message(self, answers: ConventionalCommitsAnswers) -> str:  # type: ignore[override]
        prefix = answers["prefix"]
        scope = answers["scope"]
        subject = answers["subject"]
        body = answers["body"]
        footer = answers["footer"]
        is_breaking_change = answers["is_breaking_change"]

        formatted_scope = f"({scope})" if scope else ""
        title = f"{prefix}{formatted_scope}"
        if is_breaking_change:
            if self.config.settings.get("breaking_change_exclamation_in_title", False):
                title = f"{title}!"
            footer = f"BREAKING CHANGE: {footer}"

        formatted_body = f"\n\n{body}" if body else ""
        formatted_footter = f"\n\n{footer}" if footer else ""

        return f"{title}: {subject}{formatted_body}{formatted_footter}"

    def example(self) -> str:
        return (
            "fix: correct minor typos in code\n"
            "\n"
            "see the issue for details on the typos fixed\n"
            "\n"
            "closes issue #12"
        )

    def schema(self) -> str:
        return (
            "<type>(<scope>): <subject>\n"
            "<BLANK LINE>\n"
            "<body>\n"
            "<BLANK LINE>\n"
            "(BREAKING CHANGE: )<footer>"
        )

    def schema_pattern(self) -> str:
        change_types = (
            "build",
            "bump",
            "chore",
            "ci",
            "docs",
            "feat",
            "fix",
            "perf",
            "refactor",
            "revert",
            "style",
            "test",
        )
        return (
            r"(?s)"  # To explicitly make . match new line
            r"(" + "|".join(change_types) + r")"  # type
            r"(\(\S+\))?"  # scope
            r"!?"
            r": "
            r"([^\n\r]+)"  # subject
            r"((\n\n.*)|(\s*))?$"
        )

    def info(self) -> str:
        filepath = Path(__file__).parent / "conventional_commits_info.txt"
        return filepath.read_text(encoding=self.config.settings["encoding"])
