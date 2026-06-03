from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping


class VersionIncrement(IntEnum):
    """Semantic versioning bump increments.

    IntEnum keeps a total order compatible with NONE < PATCH < MINOR < MAJOR
    for comparisons across the codebase.

    - NONE: no bump (docs-only / style commits, etc.)
    - PATCH: backwards-compatible bug fixes
    - MINOR: backwards-compatible features
    - MAJOR: incompatible API changes
    """

    NONE = 0
    PATCH = 1
    MINOR = 2
    MAJOR = 3

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_value(cls, value: object) -> VersionIncrement:
        if not isinstance(value, str):
            return VersionIncrement.NONE
        try:
            return cls[value]
        except KeyError:
            return VersionIncrement.NONE

    # Alias kept for the new ``BumpRule`` / ``CustomBumpRule`` API in
    # ``commitizen.bump_rule``. The two names do the same thing; ``safe_cast``
    # is the wording used in the bump rule plumbing while ``from_value``
    # is the wording used in the version command.
    safe_cast = from_value

    @staticmethod
    def safe_cast_dict(d: Mapping[str, object]) -> dict[str, VersionIncrement]:
        """Cast every value in ``d`` to a :class:`VersionIncrement`, dropping entries
        whose value is not one of the recognised names (``"MAJOR"``, ``"MINOR"``,
        ``"PATCH"``, ``"NONE"``).

        Entries with unrecognised string values (e.g. typos like ``"MNIOR"``) are
        silently dropped. Values that successfully cast to ``VersionIncrement.NONE``
        are also dropped because they don't contribute to a bump.

        Iteration order of the input mapping is preserved.
        """
        return {
            k: v
            for k, v in ((k, VersionIncrement.safe_cast(v)) for k, v in d.items())
            if v is not VersionIncrement.NONE
        }

    @staticmethod
    def get_highest_by_messages(
        commit_messages: Iterable[str],
        extract_increment: Callable[[str], VersionIncrement],
    ) -> VersionIncrement:
        """Find the highest version increment from a list of messages.

        This function processes a list of messages and determines the highest version
        increment needed based on the commit messages. It splits multi-line commit messages
        and evaluates each line using the provided extract_increment callable.

        Args:
            commit_messages: A list of messages to analyze.
            extract_increment: A callable that takes a commit message string and returns an
                VersionIncrement value (MAJOR, MINOR, PATCH) or NONE if no increment is needed.

        Returns:
            The highest version increment needed (MAJOR, MINOR, PATCH) or NONE if no
            increment is needed. The order of precedence is MAJOR > MINOR > PATCH.
        """
        increments = (
            extract_increment(line)
            for message in commit_messages
            for line in message.split("\n")
        )
        return max(increments, default=VersionIncrement.NONE)
