from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections.abc import Iterable, Mapping
from functools import cached_property
from typing import Any, Callable, Protocol

from jinja2 import BaseLoader, PackageLoader
from prompt_toolkit.styles import Style, merge_styles

from commitizen import git
from commitizen.bump_rule import BumpRule, CustomBumpRule, VersionIncrement
from commitizen.config.base_config import BaseConfig
from commitizen.exceptions import NoPatternMapError
from commitizen.question import CzQuestion


class MessageBuilderHook(Protocol):
    def __call__(
        self, message: dict[str, Any], commit: git.GitCommit
    ) -> dict[str, Any] | Iterable[dict[str, Any]] | None: ...


class ChangelogReleaseHook(Protocol):
    def __call__(
        self, release: dict[str, Any], tag: git.GitTag | None
    ) -> dict[str, Any]: ...


class BaseCommitizen(metaclass=ABCMeta):
    _bump_rule: BumpRule | None = None

    # TODO: decide if these should be removed
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

    def __init__(self, config: BaseConfig) -> None:
        self.config = config
        if not self.config.settings.get("style"):
            self.config.settings.update({"style": BaseCommitizen.default_style_config})

    @abstractmethod
    def questions(self) -> Iterable[CzQuestion]:
        """Questions regarding the commit message."""

    @abstractmethod
    def message(self, answers: Mapping[str, Any]) -> str:
        """Format your git message."""

    @property
    def style(self) -> Style:
        return merge_styles(
            [
                Style(BaseCommitizen.default_style_config),
                Style(self.config.settings["style"]),
            ]
        )  # type: ignore[return-value]

    @cached_property
    def bump_rule(self) -> BumpRule:
        """Get the bump rule for version incrementing.

        This property returns a BumpRule instance that determines how version numbers
        should be incremented based on commit messages. It first checks if a custom
        bump rule was set via `_bump_rule`. If not, it falls back to creating a
        CustomBumpRule using the class's bump pattern and maps.

        The CustomBumpRule requires three components to be defined:
        - bump_pattern: A regex pattern to match commit messages
        - bump_map: A mapping of commit types to version increments
        - bump_map_major_version_zero: A mapping for version increments when major version is 0

        Returns:
            BumpRule: A rule instance that determines version increments

        Raises:
            NoPatternMapError: If the required bump pattern or maps are not defined
        """
        if self._bump_rule:
            return self._bump_rule

        # Fallback to custom bump rule if no bump rule is provided
        if (
            not self.bump_pattern
            or not self.bump_map
            or not self.bump_map_major_version_zero
        ):
            raise NoPatternMapError(
                f"'{self.config.settings['name']}' rule does not support bump: {self.bump_pattern=}, {self.bump_map=}, {self.bump_map_major_version_zero=}"
            )
        return CustomBumpRule(
            self.bump_pattern,
            VersionIncrement.safe_cast_dict(self.bump_map),
            VersionIncrement.safe_cast_dict(self.bump_map_major_version_zero),
        )

    def example(self) -> str:
        """Example of the commit message."""
        raise NotImplementedError("Not Implemented yet")

    def schema(self) -> str:
        """Schema definition of the commit message."""
        raise NotImplementedError("Not Implemented yet")

    def schema_pattern(self) -> str:
        """Regex matching the schema used for message validation."""
        raise NotImplementedError("Not Implemented yet")

    def info(self) -> str:
        """Information about the standardized commit message."""
        raise NotImplementedError("Not Implemented yet")
