from __future__ import annotations

import os
from abc import ABCMeta
from re import Pattern
from typing import IO, Any, ClassVar

from commitizen.changelog import Metadata
from commitizen.config.base_config import BaseConfig
from commitizen.version_schemes import get_version_scheme

from . import ChangelogFormat


class BaseFormat(ChangelogFormat, metaclass=ABCMeta):
    """
    Base class to extend to implement a changelog file format.
    """

    extension: ClassVar[str] = ""
    alternative_extensions: ClassVar[set[str]] = set()

    def __init__(self, config: BaseConfig):
        # Constructor needs to be redefined because `Protocol` prevent instantiation by default
        # See: https://bugs.python.org/issue44807
        self.config = config

    @property
    def version_parser(self) -> Pattern:
        return get_version_scheme(self.config).parser

    def get_metadata(self, filepath: str) -> Metadata:
        if not os.path.isfile(filepath):
            return Metadata()

        with open(filepath) as changelog_file:
            return self.get_metadata_from_file(changelog_file)

    def get_metadata_from_file(self, file: IO[Any]) -> Metadata:
        meta = Metadata()
        unreleased_level: int | None = None
        for index, line in enumerate(file):
            line = line.strip().lower()

            unreleased: int | None = None
            if "unreleased" in line:
                unreleased = self.parse_title_level(line)
            # Try to find beginning and end lines of the unreleased block
            if unreleased:
                meta.unreleased_start = index
                unreleased_level = unreleased
                continue
            elif unreleased_level and self.parse_title_level(line) == unreleased_level:
                meta.unreleased_end = index

            # Try to find the latest release done
            version = self.parse_version_from_title(line)
            if version:
                meta.latest_version = version
                meta.latest_version_position = index
                break  # there's no need for more info
        if meta.unreleased_start is not None and meta.unreleased_end is None:
            meta.unreleased_end = index

        return meta

    def parse_version_from_title(self, line: str) -> str | None:
        """
        Extract the version from a title line if any
        """
        raise NotImplementedError(
            "Default `get_metadata_from_file` requires `parse_version_from_changelog` to be implemented"
        )

    def parse_title_level(self, line: str) -> int | None:
        """
        Get the title level/type of a line if any
        """
        raise NotImplementedError(
            "Default `get_metadata_from_file` requires `parse_title_type_of_line` to be implemented"
        )
