from __future__ import annotations

import os
from abc import ABCMeta
from typing import IO, ClassVar

from commitizen.changelog import Metadata
from commitizen.config.base_config import BaseConfig
from commitizen.tags import TagRules, VersionTag
from commitizen.version_schemes import get_version_scheme

from . import ChangelogFormat


class BaseFormat(ChangelogFormat, metaclass=ABCMeta):
    """
    Base class to extend to implement a changelog file format.
    """

    extension: ClassVar[str] = ""
    alternative_extensions: ClassVar[set[str]] = set()

    def __init__(self, config: BaseConfig) -> None:
        # Constructor needs to be redefined because `Protocol` prevent instantiation by default
        # See: https://bugs.python.org/issue44807
        self.config = config
        self.tag_rules = TagRules(
            scheme=get_version_scheme(self.config.settings),
            tag_format=self.config.settings["tag_format"],
            legacy_tag_formats=self.config.settings["legacy_tag_formats"],
            ignored_tag_formats=self.config.settings["ignored_tag_formats"],
        )

    def get_metadata(self, filepath: str) -> Metadata:
        if not os.path.isfile(filepath):
            return Metadata()

        with open(
            filepath, encoding=self.config.settings["encoding"]
        ) as changelog_file:
            return self.get_metadata_from_file(changelog_file)

    def get_metadata_from_file(self, file: IO[str]) -> Metadata:
        out_metadata = Metadata()
        unreleased_level: int | None = None

        lines = [line.strip().lower() for line in file.readlines()]
        for index, line in enumerate(lines):
            parsed_unreleased_level = self.parse_title_level(line)
            current_unreleased_level = (
                parsed_unreleased_level if "unreleased" in line else None
            )

            # Try to find beginning and end lines of the unreleased block
            if current_unreleased_level:
                out_metadata.unreleased_start = index
                unreleased_level = current_unreleased_level
                continue

            if unreleased_level and parsed_unreleased_level == unreleased_level:
                out_metadata.unreleased_end = index

            # Try to find the latest release done
            if parsed_version_tag := self.parse_version_from_title(line):
                out_metadata.latest_version = parsed_version_tag.version
                out_metadata.latest_version_tag = parsed_version_tag.tag
                out_metadata.latest_version_position = index
                break  # there's no need for more info

        if (
            out_metadata.unreleased_start is not None
            and out_metadata.unreleased_end is None
        ):
            out_metadata.unreleased_end = len(lines) - 1

        return out_metadata

    def parse_version_from_title(self, line: str) -> VersionTag | None:
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
