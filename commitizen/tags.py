import sys
from string import Template
from typing import Any, Optional, Type, Union

from packaging.version import Version

if sys.version_info >= (3, 8):
    from commitizen.version_types import VersionProtocol
else:
    # workaround mypy issue for 3.7 python
    VersionProtocol = Any


def tag_from_version(
    version: Union[VersionProtocol, str],
    tag_format: str,
    version_type_cls: Optional[Type[VersionProtocol]] = None,
) -> str:
    """The tag and the software version might be different.

    That's why this function exists.

    Example:
    | tag | version (PEP 0440) |
    | --- | ------- |
    | v0.9.0 | 0.9.0 |
    | ver1.0.0 | 1.0.0 |
    | ver1.0.0.a0 | 1.0.0a0 |
    """
    if version_type_cls is None:
        version_type_cls = Version
    if isinstance(version, str):
        version = version_type_cls(version)

    major, minor, patch = version.release
    prerelease = ""
    # version.pre is needed for mypy check
    if version.is_prerelease and version.pre:
        prerelease = f"{version.pre[0]}{version.pre[1]}"

    t = Template(tag_format)
    return t.safe_substitute(
        version=version, major=major, minor=minor, patch=patch, prerelease=prerelease
    )
