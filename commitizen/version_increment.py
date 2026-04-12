from __future__ import annotations

from enum import IntEnum


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
