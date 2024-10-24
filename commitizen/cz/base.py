from __future__ import annotations

import re
from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Iterable, Protocol

from jinja2 import BaseLoader, PackageLoader
from prompt_toolkit.styles import Style, merge_styles

from commitizen import git
from commitizen.config.base_config import BaseConfig
from commitizen.defaults import Questions


class MessageBuilderHook(Protocol):
    def __call__(
        self, message: dict[str, Any], commit: git.GitCommit
    ) -> dict[str, Any] | Iterable[dict[str, Any]] | None: ...


class ChangelogReleaseHook(Protocol):
    def __call__(
        self, release: dict[str, Any], tag: git.GitTag | None
    ) -> dict[str, Any]: ...


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
    changelog_message_builder_hook: MessageBuilderHook | None = None

    # Executed only at the end of the changelog generation
    changelog_hook: Callable[[str, str | None], str] | None = None

    # Executed for each release in the changelog
    changelog_release_hook: ChangelogReleaseHook | None = None

    # Plugins can override templates and provide extra template data
    template_loader: BaseLoader = PackageLoader("commitizen", "templates")
    template_extras: dict[str, Any] = {}

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

    def validate_commit_message(
        self,
        commit_msg: str,
        pattern: str | None,
        allow_abort: bool,
        allowed_prefixes: list[str],
        max_msg_length: int,
    ) -> tuple[bool, list]:
        """Validate commit message against the pattern."""
        if not commit_msg:
            return allow_abort, []

        if pattern is None:
            return True, []

        if any(map(commit_msg.startswith, allowed_prefixes)):
            return True, []
        if max_msg_length:
            msg_len = len(commit_msg.partition("\n")[0].strip())
            if msg_len > max_msg_length:
                return False, []
        return bool(re.match(pattern, commit_msg)), []

    def format_exception_message(
        self, ill_formated_commits: list[tuple[git.GitCommit, list]]
    ) -> str:
        """Format commit errors."""
        displayed_msgs_content = "\n".join(
            [
                f'commit "{commit.rev}": "{commit.message}"'
                for commit, _ in ill_formated_commits
            ]
        )
        return (
            "commit validation: failed!\n"
            "please enter a commit message in the commitizen format.\n"
            f"{displayed_msgs_content}\n"
            f"pattern: {self.schema_pattern()}"
        )

    def info(self) -> str | None:
        """Information about the standardized commit message."""
        raise NotImplementedError("Not Implemented yet")

    def process_commit(self, commit: str) -> str:
        """Process commit for changelog.

        If not overwritten, it returns the first line of commit.
        """
        return commit.split("\n")[0]
