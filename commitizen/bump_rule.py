from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from enum import IntEnum, auto
from functools import cached_property
from typing import Callable, Protocol

from commitizen.exceptions import NoPatternMapError


class VersionIncrement(IntEnum):
    """An enumeration representing semantic versioning increments.

    This class defines the three types of version increments according to semantic versioning:
    - PATCH: For backwards-compatible bug fixes
    - MINOR: For backwards-compatible functionality additions
    - MAJOR: For incompatible API changes
    """

    PATCH = auto()
    MINOR = auto()
    MAJOR = auto()

    def __str__(self) -> str:
        return self.name

    @classmethod
    def safe_cast(cls, value: object) -> VersionIncrement | None:
        if not isinstance(value, str):
            return None
        try:
            return cls[value]
        except KeyError:
            return None

    @classmethod
    def safe_cast_dict(cls, d: Mapping[str, object]) -> dict[str, VersionIncrement]:
        return {
            k: v
            for k, v in ((k, VersionIncrement.safe_cast(v)) for k, v in d.items())
            if v is not None
        }

    @staticmethod
    def get_highest_by_messages(
        commit_messages: Iterable[str],
        get_increment: Callable[[str], VersionIncrement | None],
    ) -> VersionIncrement | None:
        """Find the highest version increment from a list of messages.

        This function processes a list of messages and determines the highest version
        increment needed based on the commit messages. It splits multi-line commit messages
        and evaluates each line using the provided get_increment callable.

        Args:
            commit_messages: A list of messages to analyze.
            get_increment: A callable that takes a commit message string and returns an
                VersionIncrement value (MAJOR, MINOR, PATCH) or None if no increment is needed.

        Returns:
            The highest version increment needed (MAJOR, MINOR, PATCH) or None if no
            increment is needed. The order of precedence is MAJOR > MINOR > PATCH.

        Example:
            >>> commit_messages = ["feat: new feature", "fix: bug fix"]
            >>> rule = ConventionalCommitBumpRule()
            >>> VersionIncrement.get_highest_by_messages(commit_messages, lambda x: rule.get_increment(x, False))
            'MINOR'
        """
        return VersionIncrement.get_highest(
            get_increment(line)
            for message in commit_messages
            for line in message.split("\n")
        )

    @staticmethod
    def get_highest(
        increments: Iterable[VersionIncrement | None],
    ) -> VersionIncrement | None:
        return max(filter(None, increments), default=None)


class BumpRule(Protocol):
    """A protocol defining the interface for version bump rules.

    This protocol specifies the contract that all version bump rule implementations must follow.
    It defines how commit messages should be analyzed to determine the appropriate semantic
    version increment.

    The protocol is used to ensure consistent behavior across different bump rule implementations,
    such as conventional commits or custom rules.
    """

    def get_increment(
        self, commit_message: str, major_version_zero: bool
    ) -> VersionIncrement | None:
        """Determine the version increment based on a commit message.

        This method analyzes a commit message to determine what kind of version increment
        is needed according to the Conventional Commits specification. It handles special
        cases for breaking changes and respects the major_version_zero flag.

        Args:
            commit_message: The commit message to analyze. Should follow conventional commit format.
            major_version_zero: If True, breaking changes will result in a MINOR version bump
                              instead of MAJOR. This is useful for projects in 0.x.x versions.

        Returns:
            VersionIncrement | None: The type of version increment needed:
                - MAJOR: For breaking changes when major_version_zero is False
                - MINOR: For breaking changes when major_version_zero is True, or for new features
                - PATCH: For bug fixes, performance improvements, or refactors
                - None: For commits that don't require a version bump (docs, style, etc.)
        """


class ConventionalCommitBumpRule(BumpRule):
    _BREAKING_CHANGE_TYPES = set(["BREAKING CHANGE", "BREAKING-CHANGE"])
    _MINOR_CHANGE_TYPES = set(["feat"])
    _PATCH_CHANGE_TYPES = set(["fix", "perf", "refactor"])

    def get_increment(
        self, commit_message: str, major_version_zero: bool
    ) -> VersionIncrement | None:
        if not (m := self._head_pattern.match(commit_message)):
            return None

        change_type = m.group("change_type")
        if m.group("bang") or change_type in self._BREAKING_CHANGE_TYPES:
            return (
                VersionIncrement.MINOR if major_version_zero else VersionIncrement.MAJOR
            )

        if change_type in self._MINOR_CHANGE_TYPES:
            return VersionIncrement.MINOR

        if change_type in self._PATCH_CHANGE_TYPES:
            return VersionIncrement.PATCH

        return None

    @cached_property
    def _head_pattern(self) -> re.Pattern:
        change_types = [
            *self._BREAKING_CHANGE_TYPES,
            *self._PATCH_CHANGE_TYPES,
            *self._MINOR_CHANGE_TYPES,
            "docs",
            "style",
            "test",
            "build",
            "ci",
        ]
        re_change_type = r"(?P<change_type>" + "|".join(change_types) + r")"
        re_scope = r"(?P<scope>\(.+\))?"
        re_bang = r"(?P<bang>!)?"
        return re.compile(f"^{re_change_type}{re_scope}{re_bang}:")


class CustomBumpRule(BumpRule):
    def __init__(
        self,
        bump_pattern: str,
        bump_map: Mapping[str, VersionIncrement],
        bump_map_major_version_zero: Mapping[str, VersionIncrement],
    ) -> None:
        """Initialize a custom bump rule for version incrementing.

        This constructor creates a rule that determines how version numbers should be
        incremented based on commit messages. It validates and compiles the provided
        pattern and maps for use in version bumping.

        The fallback logic is used for backward compatibility.

        Args:
            bump_pattern: A regex pattern string used to match commit messages.
                Example: r"^((?P<major>major)|(?P<minor>minor)|(?P<patch>patch))(?P<scope>\(.+\))?(?P<bang>!)?:"
                Or with fallback regex: r"^((BREAKING[\-\ ]CHANGE|\w+)(\(.+\))?!?):"  # First group is type
            bump_map: A mapping of commit types to their corresponding version increments.
                Example: {
                    "major": VersionIncrement.MAJOR,
                    "bang": VersionIncrement.MAJOR,
                    "minor": VersionIncrement.MINOR,
                    "patch": VersionIncrement.PATCH
                }
                Or with fallback: {
                    (r"^.+!$", VersionIncrement.MAJOR),
                    (r"^BREAKING[\-\ ]CHANGE", VersionIncrement.MAJOR),
                    (r"^feat", VersionIncrement.MINOR),
                    (r"^fix", VersionIncrement.PATCH),
                    (r"^refactor", VersionIncrement.PATCH),
                    (r"^perf", VersionIncrement.PATCH),
                }
            bump_map_major_version_zero: A mapping of commit types to version increments
                specifically for when the major version is 0. This allows for different
                versioning behavior during initial development.
                The format is the same as bump_map.
                Example: {
                    "major": VersionIncrement.MINOR,  # MAJOR becomes MINOR in version zero
                    "bang": VersionIncrement.MINOR,   # Breaking changes become MINOR in version zero
                    "minor": VersionIncrement.MINOR,
                    "patch": VersionIncrement.PATCH
                }
                Or with fallback: {
                    (r"^.+!$", VersionIncrement.MINOR),
                    (r"^BREAKING[\-\ ]CHANGE", VersionIncrement.MINOR),
                    (r"^feat", VersionIncrement.MINOR),
                    (r"^fix", VersionIncrement.PATCH),
                    (r"^refactor", VersionIncrement.PATCH),
                    (r"^perf", VersionIncrement.PATCH),
                }

        Raises:
            NoPatternMapError: If any of the required parameters are empty or None
        """
        if not bump_map or not bump_pattern or not bump_map_major_version_zero:
            raise NoPatternMapError(
                f"Invalid bump rule: {bump_pattern=} and {bump_map=} and {bump_map_major_version_zero=}"
            )

        self.bump_pattern = re.compile(bump_pattern)
        self.bump_map = bump_map
        self.bump_map_major_version_zero = bump_map_major_version_zero

    def get_increment(
        self, commit_message: str, major_version_zero: bool
    ) -> VersionIncrement | None:
        if not (m := self.bump_pattern.search(commit_message)):
            return None

        effective_bump_map = (
            self.bump_map_major_version_zero if major_version_zero else self.bump_map
        )

        try:
            if ret := VersionIncrement.get_highest(
                (
                    increment
                    for name, increment in effective_bump_map.items()
                    if m.group(name)
                ),
            ):
                return ret
        except IndexError:
            pass

        # Fallback to legacy bump rule, for backward compatibility
        found_keyword = m.group(1)
        for match_pattern, increment in effective_bump_map.items():
            if re.match(match_pattern, found_keyword):
                return increment
        return None
