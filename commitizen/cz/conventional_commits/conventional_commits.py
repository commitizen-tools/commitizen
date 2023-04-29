import os
import re
from typing import IO, Any, Optional

from commitizen import defaults
from commitizen.changelog import Metadata
from commitizen.cz.base import BaseCommitizen
from commitizen.cz.utils import multiple_line_breaker, required_validator
from commitizen.defaults import Questions

__all__ = ["ConventionalCommitsCz"]


def parse_scope(text):
    if not text:
        return ""

    scope = text.strip().split()
    if len(scope) == 1:
        return scope[0]

    return "-".join(scope)


def parse_subject(text):
    if isinstance(text, str):
        text = text.strip(".").strip()

    return required_validator(text, msg="Subject is required.")


class ConventionalCommitsCz(BaseCommitizen):
    bump_pattern = defaults.bump_pattern
    bump_map = defaults.bump_map
    bump_map_major_version_zero = defaults.bump_map_major_version_zero
    commit_parser = defaults.commit_parser
    change_type_map = {
        "feat": "Feat",
        "fix": "Fix",
        "refactor": "Refactor",
        "perf": "Perf",
    }
    changelog_pattern = defaults.bump_pattern

    def questions(self) -> Questions:
        questions: Questions = [
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
                        "name": (
                            "test: Adding missing or correcting " "existing tests"
                        ),
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
                            "ci: Changes to our CI configuration files and "
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
                "filter": parse_scope,
            },
            {
                "type": "input",
                "name": "subject",
                "filter": parse_subject,
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
                "message": "Is this a BREAKING CHANGE? Correlates with MAJOR in SemVer",
                "name": "is_breaking_change",
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
        return questions

    def message(self, answers: dict) -> str:
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

        message = f"{prefix}{scope}: {subject}{body}{footer}"

        return message

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
        PATTERN = (
            r"(?s)"  # To explicitly make . match new line
            r"(build|ci|docs|feat|fix|perf|refactor|style|test|chore|revert|bump)"  # type
            r"(\(\S+\))?!?:"  # scope
            r"( [^\n\r]+)"  # subject
            r"((\n\n.*)|(\s*))?$"
        )
        return PATTERN

    def info(self) -> str:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(dir_path, "conventional_commits_info.txt")
        with open(filepath, "r", encoding=self.config.settings["encoding"]) as f:
            content = f.read()
        return content

    def process_commit(self, commit: str) -> str:
        pat = re.compile(self.schema_pattern())
        m = re.match(pat, commit)
        if m is None:
            return ""
        return m.group(3).strip()


class ConventionalCommitsTextile(ConventionalCommitsCz):
    changelog_file = "CHANGELOG.textile"

    def parse_version_from_changelog(self, line: str) -> Optional[str]:
        if not line.startswith("h2. "):
            return None
        m = re.search(defaults.version_parser, line)
        if not m:
            return None
        return m.groupdict().get("version")

    def parse_title_type_of_line(self, line: str) -> Optional[str]:
        md_title_parser = r"^(?P<title>h\d\. )"
        m = re.search(md_title_parser, line)
        if not m:
            return None
        return m.groupdict().get("title")


class ConventionalCommitsAsciiDoc(ConventionalCommitsCz):
    changelog_file = "CHANGELOG.adoc"

    def parse_version_from_changelog(self, line: str) -> Optional[str]:
        if not line.startswith("== "):
            return None
        m = re.search(defaults.version_parser, line)
        if not m:
            return None
        return m.groupdict().get("version")

    def parse_title_type_of_line(self, line: str) -> Optional[str]:
        md_title_parser = r"^(?P<title>=+)"
        m = re.search(md_title_parser, line)
        if not m:
            return None
        return m.groupdict().get("title")


class ConventionalCommitsRst(ConventionalCommitsCz):
    changelog_file = "CHANGELOG.rst"

    def get_metadata_from_file(self, file: IO[Any]) -> Metadata:
        """
        RestructuredText section titles are not one-line-based,
        it requires its own algorithm.

        This method does not extract metadata from any restructuredtext file
        but only from the one generated by this plugin with its template.

        For a more generic approach, you need to rely on `docutils`.
        """
        meta = Metadata()
        unreleased_title: Optional[str] = None
        lines = file.readlines()
        for index, (line, next_line) in enumerate(zip(lines, lines[1:])):
            line = line.strip().lower()
            next_line = next_line.strip()

            unreleased: Optional[str] = None
            if "unreleased" in line:
                unreleased = self.title_type_of_line(line, next_line)
            # Try to find beginning and end lines of the unreleased block
            if unreleased:
                meta.unreleased_start = index
                unreleased_title = unreleased
                continue
            elif (
                isinstance(unreleased_title, str)
                and self.title_type_of_line(line, next_line) == unreleased_title
            ):
                meta.unreleased_end = index

            # Try to find the latest release done
            version = self.version_from_changelog(line, next_line)
            if version:
                meta.latest_version = version
                meta.latest_version_position = index
                break  # there's no need for more info
        if meta.unreleased_start is not None and meta.unreleased_end is None:
            meta.unreleased_end = index + 1

        return meta

    def version_from_changelog(self, line: str, next_line: str) -> Optional[str]:
        if not len(next_line) >= len(line):
            return None
        elif not next_line == "=" * len(next_line):
            return None
        m = re.search(defaults.version_parser, line)
        if not m:
            return None
        return m.groupdict().get("version")

    def title_type_of_line(self, line: str, next_line: str) -> Optional[str]:
        if not len(next_line) >= len(line):
            return None
        elif not next_line == "=" * len(next_line):
            return None
        return next_line[0]
