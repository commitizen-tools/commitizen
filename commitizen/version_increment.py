from enum import IntEnum


class VersionIncrement(IntEnum):
    """An enumeration representing semantic versioning increments.
    This class defines the four types of version increments according to semantic versioning:
    - NONE: For commits that don't require a version bump (docs, style, etc.)
    - PATCH: For backwards-compatible bug fixes
    - MINOR: For backwards-compatible functionality additions
    - MAJOR: For incompatible API changes
    """

    NONE = 0
    PATCH = 1
    MINOR = 2
    MAJOR = 3

    def __str__(self) -> str:
        return self.name

    @classmethod
    def safe_cast(cls, value: object) -> "VersionIncrement":
        if not isinstance(value, str):
            return VersionIncrement.NONE
        try:
            return cls[value]
        except KeyError:
            return VersionIncrement.NONE
