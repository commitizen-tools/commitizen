from __future__ import annotations

import re
import sys
import warnings
from itertools import zip_longest
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, Type, cast, runtime_checkable

import importlib_metadata as metadata
from packaging.version import InvalidVersion  # noqa: F401: Rexpose the common exception
from packaging.version import Version as _BaseVersion

from commitizen.config.base_config import BaseConfig
from commitizen.defaults import MAJOR, MINOR, PATCH
from commitizen.exceptions import VersionSchemeUnknown

if TYPE_CHECKING:
    # TypeAlias is Python 3.10+ but backported in typing-extensions
    if sys.version_info >= (3, 10):
        from typing import TypeAlias
    else:
        from typing_extensions import TypeAlias

    # Self is Python 3.11+ but backported in typing-extensions
    if sys.version_info < (3, 11):
        from typing_extensions import Self
    else:
        from typing import Self


DEFAULT_VERSION_PARSER = r"v?(?P<version>([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+)?(\w+)?)"


@runtime_checkable
class VersionProtocol(Protocol):
    parser: ClassVar[re.Pattern]
    """Regex capturing this version scheme into a `version` group"""

    def __init__(self, version: str):
        """
        Initialize a version object from its string representation.

        :raises InvalidVersion: If the ``version`` does not conform to the scheme in any way.
        """
        raise NotImplementedError("must be implemented")

    def __str__(self) -> str:
        """A string representation of the version that can be rounded-tripped."""
        raise NotImplementedError("must be implemented")

    @property
    def scheme(self) -> VersionScheme:
        """The version scheme this version follows."""
        raise NotImplementedError("must be implemented")

    @property
    def release(self) -> tuple[int, ...]:
        """The components of the "release" segment of the version."""
        raise NotImplementedError("must be implemented")

    @property
    def is_prerelease(self) -> bool:
        """Whether this version is a pre-release."""
        raise NotImplementedError("must be implemented")

    @property
    def prerelease(self) -> str | None:
        """The prelease potion of the version is this is a prerelease."""
        raise NotImplementedError("must be implemented")

    @property
    def public(self) -> str:
        """The public portion of the version."""
        raise NotImplementedError("must be implemented")

    @property
    def local(self) -> str | None:
        """The local version segment of the version."""
        raise NotImplementedError("must be implemented")

    @property
    def major(self) -> int:
        """The first item of :attr:`release` or ``0`` if unavailable."""
        raise NotImplementedError("must be implemented")

    @property
    def minor(self) -> int:
        """The second item of :attr:`release` or ``0`` if unavailable."""
        raise NotImplementedError("must be implemented")

    @property
    def micro(self) -> int:
        """The third item of :attr:`release` or ``0`` if unavailable."""
        raise NotImplementedError("must be implemented")

    def __lt__(self, other: Any) -> bool:
        raise NotImplementedError("must be implemented")

    def __le__(self, other: Any) -> bool:
        raise NotImplementedError("must be implemented")

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError("must be implemented")

    def __ge__(self, other: Any) -> bool:
        raise NotImplementedError("must be implemented")

    def __gt__(self, other: Any) -> bool:
        raise NotImplementedError("must be implemented")

    def __ne__(self, other: object) -> bool:
        raise NotImplementedError("must be implemented")

    def bump(
        self,
        increment: str,
        prerelease: str | None = None,
        prerelease_offset: int = 0,
        devrelease: int | None = None,
        is_local_version: bool = False,
        build_metadata: str | None = None,
        force_bump: bool = False,
    ) -> Self:
        """
        Based on the given increment, generate the next bumped version according to the version scheme
        """


# With PEP 440 and SemVer semantic, Scheme is the type, Version is an instance
Version: TypeAlias = VersionProtocol
VersionScheme: TypeAlias = Type[VersionProtocol]


class BaseVersion(_BaseVersion):
    """
    A base class implementing the `VersionProtocol` for PEP440-like versions.
    """

    parser: ClassVar[re.Pattern] = re.compile(DEFAULT_VERSION_PARSER)
    """Regex capturing this version scheme into a `version` group"""

    @property
    def scheme(self) -> VersionScheme:
        return self.__class__

    @property
    def prerelease(self) -> str | None:
        # version.pre is needed for mypy check
        if self.is_prerelease and self.pre:
            return f"{self.pre[0]}{self.pre[1]}"
        return None

    def generate_prerelease(
        self, prerelease: str | None = None, offset: int = 0
    ) -> str:
        """Generate prerelease

        X.YaN   # Alpha release
        X.YbN   # Beta release
        X.YrcN  # Release Candidate
        X.Y  # Final

        This function might return something like 'alpha1'
        but it will be handled by Version.
        """
        if not prerelease:
            return ""

        # prevent down-bumping the pre-release phase, e.g. from 'b1' to 'a2'
        # https://packaging.python.org/en/latest/specifications/version-specifiers/#pre-releases
        # https://semver.org/#spec-item-11
        if self.is_prerelease and self.pre:
            prerelease = max(prerelease, self.pre[0])

        # version.pre is needed for mypy check
        if self.is_prerelease and self.pre and prerelease.startswith(self.pre[0]):
            prev_prerelease: int = self.pre[1]
            new_prerelease_number = prev_prerelease + 1
        else:
            new_prerelease_number = offset
        pre_version = f"{prerelease}{new_prerelease_number}"
        return pre_version

    def generate_devrelease(self, devrelease: int | None) -> str:
        """Generate devrelease

        The devrelease version should be passed directly and is not
        inferred based on the previous version.
        """
        if devrelease is None:
            return ""

        return f"dev{devrelease}"

    def generate_build_metadata(self, build_metadata: str | None) -> str:
        """Generate build-metadata

        Build-metadata (local version) is not used in version calculations
        but added after + statically.
        """
        if build_metadata is None:
            return ""

        return f"+{build_metadata}"

    def increment_base(self, increment: str | None = None) -> str:
        prev_release = list(self.release)
        increments = [MAJOR, MINOR, PATCH]
        base = dict(zip_longest(increments, prev_release, fillvalue=0))

        if increment == MAJOR:
            base[MAJOR] += 1
            base[MINOR] = 0
            base[PATCH] = 0
        elif increment == MINOR:
            base[MINOR] += 1
            base[PATCH] = 0
        elif increment == PATCH:
            base[PATCH] += 1

        return f"{base[MAJOR]}.{base[MINOR]}.{base[PATCH]}"

    def bump(
        self,
        increment: str,
        prerelease: str | None = None,
        prerelease_offset: int = 0,
        devrelease: int | None = None,
        is_local_version: bool = False,
        build_metadata: str | None = None,
        force_bump: bool = False,
    ) -> Self:
        """Based on the given increment a proper semver will be generated.

        For now the rules and versioning scheme is based on
        python's PEP 0440.
        More info: https://www.python.org/dev/peps/pep-0440/

        Example:
            PATCH 1.0.0 -> 1.0.1
            MINOR 1.0.0 -> 1.1.0
            MAJOR 1.0.0 -> 2.0.0
        """

        if self.local and is_local_version:
            local_version = self.scheme(self.local).bump(increment)
            return self.scheme(f"{self.public}+{local_version}")  # type: ignore
        else:
            if not self.is_prerelease:
                base = self.increment_base(increment)
            elif force_bump:
                base = self.increment_base(increment)
            else:
                base = f"{self.major}.{self.minor}.{self.micro}"
                if increment == PATCH:
                    pass
                elif increment == MINOR:
                    if self.micro != 0:
                        base = self.increment_base(increment)
                elif increment == MAJOR:
                    if self.minor != 0 or self.micro != 0:
                        base = self.increment_base(increment)
            dev_version = self.generate_devrelease(devrelease)

            release = list(self.release)
            if len(release) < 3:
                release += [0] * (3 - len(release))
            current_base = ".".join(str(part) for part in release)
            if base == current_base:
                pre_version = self.generate_prerelease(
                    prerelease, offset=prerelease_offset
                )
            else:
                base_version = cast(BaseVersion, self.scheme(base))
                pre_version = base_version.generate_prerelease(
                    prerelease, offset=prerelease_offset
                )
            build_metadata = self.generate_build_metadata(build_metadata)
            # TODO: post version
            return self.scheme(f"{base}{pre_version}{dev_version}{build_metadata}")  # type: ignore


class Pep440(BaseVersion):
    """
    PEP 440 Version Scheme

    See: https://peps.python.org/pep-0440/
    """


class SemVer(BaseVersion):
    """
    Semantic Versioning (SemVer) scheme

    See: https://semver.org/
    """

    def __str__(self) -> str:
        parts = []

        # Epoch
        if self.epoch != 0:
            parts.append(f"{self.epoch}!")

        # Release segment
        parts.append(".".join(str(x) for x in self.release))

        # Pre-release
        if self.pre:
            pre = "".join(str(x) for x in self.pre)
            parts.append(f"-{pre}")

        # Post-release
        if self.post is not None:
            parts.append(f"-post{self.post}")

        # Development release
        if self.dev is not None:
            parts.append(f"-dev{self.dev}")

        # Local version segment
        if self.local:
            parts.append(f"+{self.local}")

        return "".join(parts)


DEFAULT_SCHEME: VersionScheme = Pep440

SCHEMES_ENTRYPOINT = "commitizen.scheme"
"""Schemes entrypoints group"""

KNOWN_SCHEMES = {ep.name for ep in metadata.entry_points(group=SCHEMES_ENTRYPOINT)}
"""All known registered version schemes"""


def get_version_scheme(config: BaseConfig, name: str | None = None) -> VersionScheme:
    """
    Get the version scheme as defined in the configuration
    or from an overridden `name`

    :raises VersionSchemeUnknown: if the version scheme is not found.
    """
    deprecated_setting: str | None = config.settings.get("version_type")
    if deprecated_setting:
        warnings.warn(
            DeprecationWarning(
                "`version_type` setting is deprecated and will be removed in commitizen 4. "
                "Please use `version_scheme` instead"
            )
        )
    name = name or config.settings.get("version_scheme") or deprecated_setting
    if not name:
        return DEFAULT_SCHEME

    try:
        (ep,) = metadata.entry_points(name=name, group=SCHEMES_ENTRYPOINT)
    except ValueError:
        raise VersionSchemeUnknown(f'Version scheme "{name}" unknown.')
    scheme = cast(VersionScheme, ep.load())

    if not isinstance(scheme, VersionProtocol):
        warnings.warn(f"Version scheme {name} does not implement the VersionProtocol")

    return scheme
