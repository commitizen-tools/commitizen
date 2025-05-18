from __future__ import annotations

import re
from collections.abc import Iterable
from enum import Enum, auto
from functools import cached_property
from typing import Any, Callable, Protocol

from commitizen.exceptions import NoPatternMapError


class SemVerIncrement(Enum):
    MAJOR = auto()
    MINOR = auto()
    PATCH = auto()

    def __str__(self) -> str:
        return self.name

    @classmethod
    def safe_cast(cls, value: str | None) -> SemVerIncrement | None:
        if value is None:
            return None
        try:
            return cls[value]
        except ValueError:
            return None

    @classmethod
    def safe_cast_dict(cls, d: dict[str, Any]) -> dict[str, SemVerIncrement]:
        return {
            k: v
            for k, v in ((k, SemVerIncrement.safe_cast(v)) for k, v in d.items())
            if v is not None
        }


_VERSION_ORDERING = dict(
    zip(
        (None, SemVerIncrement.PATCH, SemVerIncrement.MINOR, SemVerIncrement.MAJOR),
        range(4),
    )
)


def find_increment_by_callable(
    commit_messages: Iterable[str],
    get_increment: Callable[[str], SemVerIncrement | None],
) -> SemVerIncrement | None:
    """Find the highest version increment from a list of messages.

    This function processes a list of messages and determines the highest version
    increment needed based on the commit messages. It splits multi-line commit messages
    and evaluates each line using the provided get_increment callable.

    Args:
        commit_messages: A list of messages to analyze.
        get_increment: A callable that takes a commit message string and returns an
            SemVerIncrement value (MAJOR, MINOR, PATCH) or None if no increment is needed.

    Returns:
        The highest version increment needed (MAJOR, MINOR, PATCH) or None if no
        increment is needed. The order of precedence is MAJOR > MINOR > PATCH.

    Example:
        >>> commit_messages = ["feat: new feature", "fix: bug fix"]
        >>> rule = ConventionalCommitBumpRule()
        >>> find_increment_by_callable(commit_messages, lambda x: rule.get_increment(x, False))
        'MINOR'
    """
    lines = (line for message in commit_messages for line in message.split("\n"))
    increments = map(get_increment, lines)
    return _find_highest_increment(increments)


def _find_highest_increment(
    increments: Iterable[SemVerIncrement | None],
) -> SemVerIncrement | None:
    return max(increments, key=lambda x: _VERSION_ORDERING[x], default=None)


class BumpRule(Protocol):
    def get_increment(
        self, commit_message: str, major_version_zero: bool
    ) -> SemVerIncrement | None:
        """Determine the version increment based on a commit message.

        This method analyzes a commit message to determine what kind of version increment
        is needed according to the Conventional Commits specification. It handles special
        cases for breaking changes and respects the major_version_zero flag.

        Args:
            commit_message: The commit message to analyze. Should follow conventional commit format.
            major_version_zero: If True, breaking changes will result in a MINOR version bump
                              instead of MAJOR. This is useful for projects in 0.x.x versions.

        Returns:
            SemVerIncrement | None: The type of version increment needed:
                - "MAJOR": For breaking changes when major_version_zero is False
                - "MINOR": For breaking changes when major_version_zero is True, or for new features
                - "PATCH": For bug fixes, performance improvements, or refactors
                - None: For commits that don't require a version bump (docs, style, etc.)
        """
        ...


class ConventionalCommitBumpRule(BumpRule):
    _PATCH_CHANGE_TYPES = set(["fix", "perf", "refactor"])
    _BREAKING_CHANGE = r"BREAKING[\-\ ]CHANGE"
    _RE_BREAKING_CHANGE = re.compile(_BREAKING_CHANGE)

    def get_increment(
        self, commit_message: str, major_version_zero: bool
    ) -> SemVerIncrement | None:
        if not (m := self._head_pattern.match(commit_message)):
            return None

        change_type = m.group("change_type")
        if m.group("bang") or self._RE_BREAKING_CHANGE.match(change_type):
            return (
                SemVerIncrement.MINOR if major_version_zero else SemVerIncrement.MAJOR
            )

        if change_type == "feat":
            return SemVerIncrement.MINOR

        if change_type in self._PATCH_CHANGE_TYPES:
            return SemVerIncrement.PATCH

        return None

    @cached_property
    def _head_pattern(self) -> re.Pattern:
        change_types = [
            self._BREAKING_CHANGE,
            "fix",
            "feat",
            "docs",
            "style",
            "refactor",
            "perf",
            "test",
            "build",
            "ci",
        ]
        re_change_type = r"(?P<change_type>" + "|".join(change_types) + r")"
        re_scope = r"(?P<scope>\(.+\))?"
        re_bang = r"(?P<bang>!)?"
        return re.compile(f"^{re_change_type}{re_scope}{re_bang}:")


class OldSchoolBumpRule(BumpRule):
    """TODO: rename?"""

    def __init__(
        self,
        bump_pattern: str,
        bump_map: dict[str, SemVerIncrement],
        bump_map_major_version_zero: dict[str, SemVerIncrement],
    ):
        if not bump_map or not bump_pattern or not bump_map_major_version_zero:
            raise NoPatternMapError(
                f"Invalid bump rule: {bump_pattern=} and {bump_map=} and {bump_map_major_version_zero=}"
            )

        self.bump_pattern = re.compile(bump_pattern)
        self.bump_map = bump_map
        self.bump_map_major_version_zero = bump_map_major_version_zero

    def get_increment(
        self, commit_message: str, major_version_zero: bool
    ) -> SemVerIncrement | None:
        if not (m := self.bump_pattern.search(commit_message)):
            return None

        bump_map = (
            self.bump_map_major_version_zero if major_version_zero else self.bump_map
        )

        try:
            if ret := _find_highest_increment(
                (increment for name, increment in bump_map.items() if m.group(name))
            ):
                return ret
        except IndexError:
            # Fallback to old school bump rule
            pass

        # Fallback to old school bump rule
        found_keyword = m.group(1)
        for match_pattern, increment in bump_map.items():
            if re.match(match_pattern, found_keyword):
                return increment
        return None
