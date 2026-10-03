"""Helpers for comparing and deriving semantic-version increments.

This module centralizes the conversion between external increment labels and the
ordered enum used internally by bump-related commands. The distinction matters
because some callers intentionally coerce unknown values to ``NONE`` while
matched ``bump_map`` outputs must preserve the historical fail-fast behavior for
invalid custom rule values.
"""

from __future__ import annotations

import re
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

RegexPattern = str | re.Pattern[str]


class VersionIncrement(IntEnum):
    """Semantic versioning bump increments.

    IntEnum keeps a total order compatible with NONE < PATCH < MINOR < MAJOR
    for comparisons across the codebase.

    - NONE: no bump (docs-only / style commits, etc.)
    - PATCH: backwards-compatible bug fixes
    - MINOR: backwards-compatible features
    - MAJOR: incompatible API changes

    Examples:
        ```python
        max([VersionIncrement.PATCH, VersionIncrement.MINOR])
        # VersionIncrement.MINOR
        ```
    """

    NONE = 0
    PATCH = 1
    MINOR = 2
    MAJOR = 3

    def __str__(self) -> str:
        """Return the legacy string representation used by existing callers."""
        return self.name

    @classmethod
    def from_value(cls, value: object) -> VersionIncrement:
        """Convert external increment input into a known increment.

        This lenient path is used for inputs such as CLI arguments where an
        unknown string should behave like "no increment" instead of raising.
        Matched ``bump_map`` values are validated separately so custom rules keep
        their historical fail-fast behavior.
        """
        if not isinstance(value, str):
            return VersionIncrement.NONE
        try:
            return cls[value]
        except KeyError:
            return VersionIncrement.NONE

    @classmethod
    def _compile_pattern(cls, regex: RegexPattern) -> re.Pattern[str]:
        """Normalize a bump-pattern input into a compiled regular expression."""
        if isinstance(regex, re.Pattern):
            return regex
        return re.compile(regex)

    @classmethod
    def _from_bump_map_value(cls, value: object) -> VersionIncrement:
        """Resolve a configured bump-map value or reject invalid rule output.

        This preserves the historical behavior where a matched custom bump-map
        entry with an unsupported increment fails immediately instead of being
        treated as a no-op.
        """
        if value is None:
            return cls.NONE
        if value == "PATCH":
            return cls.PATCH
        if value == "MINOR":
            return cls.MINOR
        if value == "MAJOR":
            return cls.MAJOR
        raise ValueError(f"Invalid bump increment: {value!r}")

    @classmethod
    def from_match(
        cls, matched_text: str, increments_map: Mapping[str, object]
    ) -> VersionIncrement:
        """Resolve one extracted bump token against a configured bump map.

        The first regular-expression key that matches wins, preserving the
        current user-visible behavior of ``bump_map`` ordering.
        """
        for match_pattern, increment in increments_map.items():
            if re.match(match_pattern, matched_text):
                return cls._from_bump_map_value(increment)
        return cls.NONE

    @classmethod
    def from_message(
        cls, message: str, regex: RegexPattern, increments_map: Mapping[str, object]
    ) -> VersionIncrement:
        """Compute the highest increment contributed by one commit message.

        Commitizen historically evaluates each line of the full commit message
        against ``bump_pattern`` and then keeps the highest resulting bump.
        This method preserves that behavior while returning a comparable enum.
        """
        select_pattern = cls._compile_pattern(regex)
        increment = cls.NONE

        for line in message.split("\n"):
            result = select_pattern.search(line)
            if not result:
                continue

            increment = max(
                increment,
                cls.from_match(result.group(1), increments_map),
            )
            if increment == cls.MAJOR:
                return increment

        return increment

    @classmethod
    def get_highest_by_messages(
        cls,
        messages: Iterable[str],
        regex: RegexPattern,
        increments_map: Mapping[str, object],
    ) -> VersionIncrement:
        """Compute the highest increment across many commit messages.

        An empty iterable yields ``NONE`` so callers can preserve the existing
        "no increment" behavior explicitly instead of relying on exceptions from
        ``max()``.
        """
        select_pattern = cls._compile_pattern(regex)
        return max(
            (
                cls.from_message(message, select_pattern, increments_map)
                for message in messages
            ),
            default=cls.NONE,
        )
