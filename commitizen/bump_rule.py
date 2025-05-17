from __future__ import annotations

import re
from functools import cached_property
from typing import Callable, Protocol

from commitizen.version_schemes import Increment

_VERSION_ORDERING = dict(zip((None, "PATCH", "MINOR", "MAJOR"), range(4)))


def find_increment_by_callable(
    commit_messages: list[str], get_increment: Callable[[str], Increment | None]
) -> Increment | None:
    """Find the highest version increment from a list of messages.

    This function processes a list of messages and determines the highest version
    increment needed based on the commit messages. It splits multi-line commit messages
    and evaluates each line using the provided get_increment callable.

    Args:
        commit_messages: A list of messages to analyze.
        get_increment: A callable that takes a commit message string and returns an
            Increment value (MAJOR, MINOR, PATCH) or None if no increment is needed.

    Returns:
        The highest version increment needed (MAJOR, MINOR, PATCH) or None if no
        increment is needed. The order of precedence is MAJOR > MINOR > PATCH.

    Example:
        >>> commit_messages = ["feat: new feature", "fix: bug fix"]
        >>> rule = DefaultBumpRule()
        >>> find_increment_by_callable(commit_messages, lambda x: rule.get_increment(x, False))
        'MINOR'
    """
    lines = (line for message in commit_messages for line in message.split("\n"))
    increments = map(get_increment, lines)
    return max(increments, key=lambda x: _VERSION_ORDERING[x], default=None)


class BumpRule(Protocol):
    def get_increment(
        self, commit_message: str, major_version_zero: bool
    ) -> Increment | None: ...


class DefaultBumpRule(BumpRule):
    _PATCH_CHANGE_TYPES = set(["fix", "perf", "refactor"])

    def get_increment(
        self, commit_message: str, major_version_zero: bool
    ) -> Increment | None:
        if not (m := self._head_pattern.match(commit_message)):
            return None

        change_type = m.group("change_type")
        if m.group("bang") or change_type == "BREAKING CHANGE":
            return "MAJOR" if major_version_zero else "MINOR"

        if change_type == "feat":
            return "MINOR"

        if change_type in self._PATCH_CHANGE_TYPES:
            return "PATCH"

        return None

    @cached_property
    def _head_pattern(self) -> re.Pattern:
        change_types = [
            r"BREAKING[\-\ ]CHANGE",
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


class CustomBumpRule(BumpRule):
    """TODO: Implement"""

    def get_increment(
        self, commit_message: str, major_version_zero: bool
    ) -> Increment | None:
        return None
