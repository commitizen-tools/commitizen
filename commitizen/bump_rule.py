from __future__ import annotations

import re
from functools import cached_property
from typing import TYPE_CHECKING, Protocol

from commitizen.exceptions import NoPatternMapError
from commitizen.version_increment import VersionIncrement

if TYPE_CHECKING:
    from collections.abc import Mapping


# Re-export for backward compatibility with code that uses
# ``from commitizen.bump_rule import VersionIncrement``.
__all__ = [
    "BumpRule",
    "ConventionalCommitBumpRule",
    "CustomBumpRule",
    "VersionIncrement",
]


class BumpRule(Protocol):
    """A protocol defining the interface for version bump rules.

    This protocol specifies the contract that all version bump rule implementations must follow.
    It defines how commit messages should be analyzed to determine the appropriate semantic
    version increment.

    The protocol is used to ensure consistent behavior across different bump rule implementations,
    such as conventional commits or custom rules.
    """

    def extract_increment(
        self, commit_message: str, major_version_zero: bool
    ) -> VersionIncrement:
        """Determine the version increment based on a commit message.

        This method analyzes a commit message to determine what kind of version increment
        is needed. It handles special cases for breaking changes and respects the major_version_zero flag.

        See the following subclasses for more details:
        - ConventionalCommitBumpRule: For conventional commits
        - CustomBumpRule: For custom bump rules

        Args:
            commit_message: The commit message to analyze.
            major_version_zero: If True, breaking changes will result in a MINOR version bump instead of MAJOR

        Returns:
            VersionIncrement: The type of version increment needed:
        """


class ConventionalCommitBumpRule(BumpRule):
    _BREAKING_CHANGE_TYPES = {"BREAKING CHANGE", "BREAKING-CHANGE"}
    _MINOR_CHANGE_TYPES = {"feat"}
    _PATCH_CHANGE_TYPES = {"fix", "perf", "refactor"}

    def extract_increment(
        self, commit_message: str, major_version_zero: bool
    ) -> VersionIncrement:
        if not (m := self._head_pattern.match(commit_message)):
            return VersionIncrement.NONE

        change_type = m.group("change_type")
        if m.group("bang") or change_type in self._BREAKING_CHANGE_TYPES:
            return (
                VersionIncrement.MINOR if major_version_zero else VersionIncrement.MAJOR
            )

        if change_type in self._MINOR_CHANGE_TYPES:
            return VersionIncrement.MINOR

        if change_type in self._PATCH_CHANGE_TYPES:
            return VersionIncrement.PATCH

        return VersionIncrement.NONE

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
        bump_map_major_version_zero: Mapping[str, VersionIncrement] | None = None,
    ) -> None:
        """Initialize a custom bump rule for version incrementing.

        This constructor creates a rule that determines how version numbers should be
        incremented based on commit messages. It validates and compiles the provided
        pattern and maps for use in version bumping.

        The fallback logic is used for backward compatibility.

        Args:
            bump_pattern: A regex pattern string used to match commit messages.
                Example: r"^((?P<major>major)|(?P<minor>minor)|(?P<patch>patch))(?P<scope>\\(.+\\))?(?P<bang>!)?:"

                Or with fallback regex: r"^((BREAKING[\\-\\ ]CHANGE|\\w+)(\\(.+\\))?!?):"  # First group is type
            bump_map: A mapping of commit types to their corresponding version increments.
                Example: {
                    "major": VersionIncrement.MAJOR,
                    "bang": VersionIncrement.MAJOR,
                    "minor": VersionIncrement.MINOR,
                    "patch": VersionIncrement.PATCH
                }
                Or with fallback: {
                    r"^.+!$": VersionIncrement.MAJOR,
                    r"^BREAKING[\\-\\ ]CHANGE": VersionIncrement.MAJOR,
                    r"^feat": VersionIncrement.MINOR,
                    r"^fix": VersionIncrement.PATCH,
                    r"^refactor": VersionIncrement.PATCH,
                    r"^perf": VersionIncrement.PATCH,
                }

                NOTE: For the fallback path, iteration order matters because the rule
                returns the first matching pattern. Python 3.7+ preserves insertion
                order for plain dicts.
            bump_map_major_version_zero: A mapping of commit types to version increments
                specifically for when the major version is 0. This allows for different
                versioning behavior during initial development. The format is the same
                as bump_map. May be ``None`` if the plugin doesn't need to bump
                differently in the ``major_version_zero`` mode; in that case calling
                ``extract_increment(..., major_version_zero=True)`` will raise
                :class:`NoPatternMapError` (matching the legacy behaviour).

        Raises:
            NoPatternMapError: If ``bump_pattern`` or ``bump_map`` is empty or ``None``.
        """
        if not bump_map or not bump_pattern:
            raise NoPatternMapError(
                f"Invalid bump rule: {bump_pattern=} and {bump_map=}"
            )

        self.bump_pattern = re.compile(bump_pattern)
        self.bump_map = bump_map
        self.bump_map_major_version_zero = bump_map_major_version_zero

    def extract_increment(
        self, commit_message: str, major_version_zero: bool
    ) -> VersionIncrement:
        if major_version_zero:
            if not self.bump_map_major_version_zero:
                raise NoPatternMapError(
                    "bump_map_major_version_zero is required when major_version_zero is True"
                )
            effective_bump_map = self.bump_map_major_version_zero
        else:
            effective_bump_map = self.bump_map

        if not (m := self.bump_pattern.search(commit_message)):
            return VersionIncrement.NONE

        try:
            increments = (
                increment
                for name, increment in effective_bump_map.items()
                if m.group(name)
            )
            increment = max(increments, default=VersionIncrement.NONE)
            if increment != VersionIncrement.NONE:
                return increment
        except IndexError:
            pass

        # Fallback to legacy bump rule, for backward compatibility.
        # Iteration order matters: returns the FIRST matching pattern.
        found_keyword = m.group(1)
        for match_pattern, increment in effective_bump_map.items():
            if re.match(match_pattern, found_keyword):
                return increment
        return VersionIncrement.NONE
