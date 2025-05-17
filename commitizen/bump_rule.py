from __future__ import annotations

import re
from functools import cached_property
from typing import Protocol

from commitizen.version_schemes import Increment


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
