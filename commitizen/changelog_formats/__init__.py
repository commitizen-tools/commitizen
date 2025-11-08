from __future__ import annotations

import sys
from typing import Callable

from commitizen.changelog_formats.base import BaseFormat

if sys.version_info >= (3, 10):
    from importlib import metadata
else:
    import importlib_metadata as metadata

from commitizen.config.base_config import BaseConfig
from commitizen.exceptions import ChangelogFormatUnknown

CHANGELOG_FORMAT_ENTRYPOINT = "commitizen.changelog_format"


KNOWN_CHANGELOG_FORMATS: dict[str, type[BaseFormat]] = {
    ep.name: ep.load()
    for ep in metadata.entry_points(group=CHANGELOG_FORMAT_ENTRYPOINT)
}


def get_changelog_format(config: BaseConfig, filename: str | None = None) -> BaseFormat:
    """
    Get a format from its name

    :raises FormatUnknown: if a non-empty name is provided but cannot be found in the known formats
    """
    name: str | None = config.settings.get("changelog_format")
    format = (
        name and KNOWN_CHANGELOG_FORMATS.get(name) or _guess_changelog_format(filename)
    )

    if not format:
        raise ChangelogFormatUnknown(f"Unknown changelog format '{name}'")

    return format(config)


def _guess_changelog_format(filename: str | None) -> type[BaseFormat] | None:
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


def __getattr__(name: str) -> Callable[[str], type[BaseFormat] | None]:
    if name == "guess_changelog_format":
        return _guess_changelog_format
    raise AttributeError(f"module {__name__} has no attribute {name}")
