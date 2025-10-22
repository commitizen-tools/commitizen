import os
from typing import TypedDict

from commitizen import defaults
from commitizen.cz.base import BaseCommitizen
from commitizen.cz.utils import multiple_line_breaker, required_validator
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
    changelog_pattern = defaults.BUMP_PATTERN

    def questions(self) -> list[CzQuestion]:
        return [
            {
                "type": "list",
                "name": "prefix",
                "message": "Select the type of change you are committing",
                "choices": [
                    {
                        "value": "fix",
                        "name": "fix: A bug fix. Correlates with PATCH in SemVer",
                        "key": "x",
                    },
                    {
                        "value": "feat",
                        "name": "feat: A new feature. Correlates with MINOR in SemVer",
                        "key": "f",
                    },
                    {
                        "value": "docs",
                        "name": "docs: Documentation only changes",
                        "key": "d",
                    },
                    {
                        "value": "style",
                        "name": (
                            "style: Changes that do not affect the "
                            "meaning of the code (white-space, formatting,"
                            " missing semi-colons, etc)"
                        ),
                        "key": "s",
                    },
                    {
                        "value": "refactor",
                        "name": (
                            "refactor: A code change that neither fixes "
                            "a bug nor adds a feature"
                        ),
                        "key": "r",
                    },
                    {
                        "value": "perf",
                        "name": "perf: A code change that improves performance",
                        "key": "p",
                    },
                    {
                        "value": "test",
                        "name": ("test: Adding missing or correcting existing tests"),
                        "key": "t",
                    },
                    {
                        "value": "build",
                        "name": (
                            "build: Changes that affect the build system or "
                            "external dependencies (example scopes: pip, docker, npm)"
                        ),
                        "key": "b",
                    },
                    {
                        "value": "ci",
                        "name": (
                            "ci: Changes to CI configuration files and "
                            "scripts (example scopes: GitLabCI)"
                        ),
                        "key": "c",
                    },
                ],
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

        if scope:
            scope = f"({scope})"
        if body:
            body = f"\n\n{body}"
        if is_breaking_change:
            footer = f"BREAKING CHANGE: {footer}"
        if footer:
            footer = f"\n\n{footer}"

        return f"{prefix}{scope}: {subject}{body}{footer}"

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
        dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(dir_path, "conventional_commits_info.txt")
        with open(filepath, encoding=self.config.settings["encoding"]) as f:
            return f.read()
