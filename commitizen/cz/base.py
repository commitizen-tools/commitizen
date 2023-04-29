from __future__ import annotations

from abc import ABCMeta, abstractmethod
import os
import re
from typing import IO, Any, Callable

from jinja2 import BaseLoader, PackageLoader
from prompt_toolkit.styles import Style, merge_styles

from commitizen import git
from commitizen import defaults
from commitizen.changelog import Metadata
from commitizen.config.base_config import BaseConfig
from commitizen.defaults import Questions


class BaseCommitizen(metaclass=ABCMeta):
    bump_pattern: str | None = None
    bump_map: dict[str, str] | None = None
    bump_map_major_version_zero: dict[str, str] | None = None
    default_style_config: list[tuple[str, str]] = [
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

    # The whole subject will be parsed as message by default
    # This allows supporting changelog for any rule system.
    # It can be modified per rule
    commit_parser: str | None = r"(?P<message>.*)"
    changelog_pattern: str | None = r".*"
    change_type_map: dict[str, str] | None = None
    change_type_order: list[str] | None = None

    # Executed per message parsed by the commitizen
    changelog_message_builder_hook: None | (
        Callable[[dict, git.GitCommit], dict]
    ) = None

    # Executed only at the end of the changelog generation
    changelog_hook: Callable[[str, str | None], str] | None = None

    changelog_file: str = "CHANGELOG.md"

    # template: str = DEFAULT_TEMPLATE
    template_loader: BaseLoader = PackageLoader("commitizen", "templates")
    template_extras: dict[str, Any] = {}

    def __init__(self, config: BaseConfig):
        self.config = config
        if not self.config.settings.get("style"):
            self.config.settings.update({"style": BaseCommitizen.default_style_config})

    @property
    def template(self) -> str:
        return f"{self.changelog_file}.j2"

    @abstractmethod
    def questions(self) -> Questions:
        """Questions regarding the commit message."""

    @abstractmethod
    def message(self, answers: dict) -> str:
        """Format your git message."""

    @property
    def style(self):
        return merge_styles(
            [
                Style(BaseCommitizen.default_style_config),
                Style(self.config.settings["style"]),
            ]
        )

    def example(self) -> str | None:
        """Example of the commit message."""
        raise NotImplementedError("Not Implemented yet")

    def schema(self) -> str | None:
        """Schema definition of the commit message."""
        raise NotImplementedError("Not Implemented yet")

    def schema_pattern(self) -> str | None:
        """Regex matching the schema used for message validation."""
        raise NotImplementedError("Not Implemented yet")

    def info(self) -> str | None:
        """Information about the standardized commit message."""
        raise NotImplementedError("Not Implemented yet")

    def process_commit(self, commit: str) -> str:
        """Process commit for changelog.

        If not overwritten, it returns the first line of commit.
        """
        return commit.split("\n")[0]

    def get_metadata(self, filepath: str) -> Metadata:
        if not os.path.isfile(filepath):
            return Metadata()

        with open(filepath, "r") as changelog_file:
            return self.get_metadata_from_file(changelog_file)

    def get_metadata_from_file(self, file: IO[Any]) -> Metadata:
        meta = Metadata()
        unreleased_title: str | None = None
        for index, line in enumerate(file):
            line = line.strip().lower()

            unreleased: str | None = None
            if "unreleased" in line:
                unreleased = self.parse_title_type_of_line(line)
            # Try to find beginning and end lines of the unreleased block
            if unreleased:
                meta.unreleased_start = index
                unreleased_title = unreleased
                continue
            elif (
                isinstance(unreleased_title, str)
                and self.parse_title_type_of_line(line) == unreleased_title
            ):
                meta.unreleased_end = index

            # Try to find the latest release done
            version = self.parse_version_from_changelog(line)
            if version:
                meta.latest_version = version
                meta.latest_version_position = index
                break  # there's no need for more info
        if meta.unreleased_start is not None and meta.unreleased_end is None:
            meta.unreleased_end = index

        return meta

    def parse_version_from_changelog(self, line: str) -> str | None:
        if not line.startswith("#"):
            return None
        m = re.search(defaults.version_parser, line)
        if not m:
            return None
        return m.groupdict().get("version")

    def parse_title_type_of_line(self, line: str) -> str | None:
        md_title_parser = r"^(?P<title>#+)"
        m = re.search(md_title_parser, line)
        if not m:
            return None
        return m.groupdict().get("title")
