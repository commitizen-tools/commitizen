import sys
from typing import Optional, Tuple, Union

if sys.version_info >= (3, 8):
    from typing import Protocol as _Protocol
else:
    _Protocol = object

from packaging.version import Version


class VersionProtocol(_Protocol):
    def __init__(self, _version: Union[Version, str]):
        raise NotImplementedError("must be implemented")

    def __str__(self) -> str:
        raise NotImplementedError("must be implemented")

    @property
    def release(self) -> Tuple[int, ...]:
        raise NotImplementedError("must be implemented")

    @property
    def is_prerelease(self) -> bool:
        raise NotImplementedError("must be implemented")

    @property
    def pre(self) -> Optional[Tuple[str, int]]:
        raise NotImplementedError("must be implemented")

    @property
    def local(self) -> Optional[str]:
        raise NotImplementedError("must be implemented")

    @property
    def public(self) -> str:
        raise NotImplementedError("must be implemented")


class SemVerVersion(VersionProtocol):
    def __init__(self, version: str):
        self._version = Version(version)

    @property
    def release(self) -> Tuple[int, ...]:
        return self._version.release

    @property
    def is_prerelease(self) -> bool:
        return self._version.is_prerelease

    @property
    def pre(self) -> Optional[Tuple[str, int]]:
        return self._version.pre

    @property
    def local(self) -> Optional[str]:
        return self._version.local

    @property
    def public(self) -> str:
        return self._version.public

    def __str__(self) -> str:
        parts = []

        version = self._version

        # Epoch
        if version.epoch != 0:
            parts.append(f"{version.epoch}!")

        # Release segment
        parts.append(".".join(str(x) for x in version.release))

        # Pre-release
        if version.pre:
            pre = "".join(str(x) for x in version.pre)
            parts.append(f"-{pre}")

        # Post-release
        if version.post is not None:
            parts.append(f"-post{version.post}")

        # Development release
        if version.dev is not None:
            parts.append(f"-dev{version.dev}")

        # Local version segment
        if version.local:
            parts.append(f"+{version.local}")

        return "".join(parts)


VERSION_TYPES = {
    "semver": SemVerVersion,
    "pep440": Version,
}
