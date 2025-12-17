from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any, NamedTuple, Protocol

from jinja2 import BaseLoader, PackageLoader
from prompt_toolkit.styles import Style

from commitizen.exceptions import CommitMessageLengthExceededError

if TYPE_CHECKING:
    import re
    from collections.abc import Callable, Iterable, Mapping

    from commitizen import git
    from commitizen.config.base_config import BaseConfig
    from commitizen.question import CzQuestion


class MessageBuilderHook(Protocol):
    def __call__(
        self, message: dict[str, Any], commit: git.GitCommit
    ) -> dict[str, Any] | Iterable[dict[str, Any]] | None: ...


class ChangelogReleaseHook(Protocol):
    def __call__(
        self, release: dict[str, Any], tag: git.GitTag | None
    ) -> dict[str, Any]: ...


class ValidationResult(NamedTuple):
    is_valid: bool
    errors: list


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

    # The whole subject will be parsed as a message by default
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

    def __init__(self, config: BaseConfig) -> None:
        self.config = config
        if not self.config.settings.get("style"):
            self.config.settings.update({"style": BaseCommitizen.default_style_config})

    @abstractmethod
    def questions(self) -> list[CzQuestion]:
        """Questions regarding the commit message."""

    @abstractmethod
    def message(self, answers: Mapping[str, Any]) -> str:
        """Format your git message."""

    @property
    def style(self) -> Style:
        return Style(
            [
                *BaseCommitizen.default_style_config,
                *self.config.settings["style"],
            ]
        )

    @abstractmethod
    def example(self) -> str:
        """Example of the commit message."""

    @abstractmethod
    def schema(self) -> str:
        """Schema definition of the commit message."""

    @abstractmethod
    def schema_pattern(self) -> str:
        """Regex matching the schema used for message validation."""

    @abstractmethod
    def info(self) -> str:
        """Information about the standardized commit message."""

    def validate_commit_message(
        self,
        *,
        commit_msg: str,
        pattern: re.Pattern[str],
        allow_abort: bool,
        allowed_prefixes: list[str],
        max_msg_length: int | None,
        commit_hash: str,
    ) -> ValidationResult:
        """Validate commit message against the pattern."""
        if not commit_msg:
            return ValidationResult(
                allow_abort, [] if allow_abort else ["commit message is empty"]
            )

        if any(map(commit_msg.startswith, allowed_prefixes)):
            return ValidationResult(True, [])

        if max_msg_length is not None:
            msg_len = len(commit_msg.partition("\n")[0].strip())
            if msg_len > max_msg_length:
                # TODO: capitalize the first letter of the error message for consistency in v5
                raise CommitMessageLengthExceededError(
                    f"commit validation: failed!\n"
                    f"commit message length exceeds the limit.\n"
                    f'commit "{commit_hash}": "{commit_msg}"\n'
                    f"message length limit: {max_msg_length} (actual: {msg_len})"
                )

        return ValidationResult(
            bool(pattern.match(commit_msg)),
            [f"pattern: {pattern.pattern}"],
        )

    def format_exception_message(
        self, invalid_commits: list[tuple[git.GitCommit, list]]
    ) -> str:
        """Format commit errors."""
        displayed_msgs_content = "\n".join(
            [
                f'commit "{commit.rev}": "{commit.message}\n"' + "\n".join(errors)
                for commit, errors in invalid_commits
            ]
        )
        # TODO: capitalize the first letter of the error message for consistency in v5
        return (
            "commit validation: failed!\n"
            "please enter a commit message in the commitizen format.\n"
            f"{displayed_msgs_content}"
        )
