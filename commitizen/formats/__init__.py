from __future__ import annotations

import sys

from typing import ClassVar, Optional

import importlib_metadata as metadata

from commitizen.changelog import Metadata
from commitizen.config.base_config import BaseConfig

from .errors import FormatUnknown

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

FORMAT_ENTRYPOINT = "commitizen.format"
DEFAULT_FORMAT = "markdown"
DEFAULT_TEMPLATE_EXTENSION = "j2"


class Format(Protocol):
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
        return f"CHANGELOG.{self.extension}.{DEFAULT_TEMPLATE_EXTENSION}"

    @property
    def default_changelog_file(self) -> str:
        return f"CHANGELOG.{self.extension}"

    def get_metadata(self, filepath: str) -> Metadata:
        """
        Extract the changelog metadata.
        """


KNOWN_FORMATS: dict[str, type[Format]] = {
    ep.name: ep.load() for ep in metadata.entry_points(group=FORMAT_ENTRYPOINT)
}


def get_format(config: BaseConfig, filename: Optional[str] = None) -> Format:
    """
    Get a format from its name

    :raises FormatUnknown: if a non-empty name is provided but cannot be found in the known formats
    """
    name: Optional[str] = config.settings.get("format")
    format: Optional[type[Format]] = guess_format(filename)

    if name and name in KNOWN_FORMATS:
        format = KNOWN_FORMATS[name]

    if not format:
        raise FormatUnknown(f"unknown format '{name}'")

    return format(config)


def guess_format(filename: Optional[str]) -> Optional[type[Format]]:
    """
    Try guessing the file format from the filename.

    Algorithm is basic, extension-based, and won't work
    for extension-less file names like `CHANGELOG` or `NEWS`.
    """
    if not filename or not isinstance(filename, str):
        return None
    for format in KNOWN_FORMATS.values():
        if filename.endswith(f".{format.extension}"):
            return format
        for alt_extension in format.alternative_extensions:
            if filename.endswith(f".{alt_extension}"):
                return format
    return None
