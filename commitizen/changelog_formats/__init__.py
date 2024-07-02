from __future__ import annotations

import sys
from typing import ClassVar, Protocol

if sys.version_info >= (3, 10):
    from importlib import metadata
else:
    import importlib_metadata as metadata

from commitizen.changelog import Metadata
from commitizen.config.base_config import BaseConfig
from commitizen.exceptions import ChangelogFormatUnknown

CHANGELOG_FORMAT_ENTRYPOINT = "commitizen.changelog_format"
TEMPLATE_EXTENSION = "j2"


class ChangelogFormat(Protocol):
    extension: ClassVar[str]
    """Standard known extension associated with this format"""

    alternative_extensions: ClassVar[set[str]]
    """Known alternatives extensions for this format"""

    config: BaseConfig

    def __init__(self, config: BaseConfig):
        self.config = config

    @property
    def ext(self) -> str:
        """Dotted version of extensions, as in `pathlib` and `os` modules"""
        return f".{self.extension}"

    @property
    def template(self) -> str:
        """Expected template name for this format"""
        return f"CHANGELOG.{self.extension}.{TEMPLATE_EXTENSION}"

    @property
    def default_changelog_file(self) -> str:
        return f"CHANGELOG.{self.extension}"

    def get_metadata(self, filepath: str) -> Metadata:
        """
        Extract the changelog metadata.
        """
        raise NotImplementedError


KNOWN_CHANGELOG_FORMATS: dict[str, type[ChangelogFormat]] = {
    ep.name: ep.load()
    for ep in metadata.entry_points(group=CHANGELOG_FORMAT_ENTRYPOINT)
}


def get_changelog_format(
    config: BaseConfig, filename: str | None = None
) -> ChangelogFormat:
    """
    Get a format from its name

    :raises FormatUnknown: if a non-empty name is provided but cannot be found in the known formats
    """
    name: str | None = config.settings.get("changelog_format")
    format: type[ChangelogFormat] | None = guess_changelog_format(filename)

    if name and name in KNOWN_CHANGELOG_FORMATS:
        format = KNOWN_CHANGELOG_FORMATS[name]

    if not format:
        raise ChangelogFormatUnknown(f"Unknown changelog format '{name}'")

    return format(config)


def guess_changelog_format(filename: str | None) -> type[ChangelogFormat] | None:
    """
    Try guessing the file format from the filename.

    Algorithm is basic, extension-based, and won't work
    for extension-less file names like `CHANGELOG` or `NEWS`.
    """
    if not filename or not isinstance(filename, str):
        return None
    for format in KNOWN_CHANGELOG_FORMATS.values():
        if filename.endswith(f".{format.extension}"):
            return format
        for alt_extension in format.alternative_extensions:
            if filename.endswith(f".{alt_extension}"):
                return format
    return None
