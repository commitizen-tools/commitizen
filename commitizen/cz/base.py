from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Callable

from prompt_toolkit.styles import Style, merge_styles

from commitizen import git
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

    def __init__(self, config: BaseConfig):
        self.config = config
        if not self.config.settings.get("style"):
            self.config.settings.update({"style": BaseCommitizen.default_style_config})

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
