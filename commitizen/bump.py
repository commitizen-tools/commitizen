from __future__ import annotations

import os
import re
from collections import OrderedDict
from glob import iglob
from logging import getLogger
from string import Template
from typing import cast

from commitizen.defaults import MAJOR, MINOR, PATCH, bump_message, encoding
from commitizen.exceptions import CurrentVersionNotFoundError
from commitizen.git import GitCommit, smart_open
from commitizen.version_schemes import Increment, Version

VERSION_TYPES = [None, PATCH, MINOR, MAJOR]

logger = getLogger("commitizen")


def find_increment(
    commits: list[GitCommit], regex: str, increments_map: dict | OrderedDict
) -> Increment | None:
    if isinstance(increments_map, dict):
        increments_map = OrderedDict(increments_map)

    # Most important cases are major and minor.
    # Everything else will be considered patch.
    select_pattern = re.compile(regex)
    increment: str | None = None

    for commit in commits:
        for message in commit.message.split("\n"):
            result = select_pattern.search(message)

            if result:
                found_keyword = result.group(1)
                new_increment = None
                for match_pattern in increments_map.keys():
                    if re.match(match_pattern, found_keyword):
                        new_increment = increments_map[match_pattern]
                        break

                if new_increment is None:
                    logger.debug(
                        f"no increment needed for '{found_keyword}' in '{message}'"
                    )

                if VERSION_TYPES.index(increment) < VERSION_TYPES.index(new_increment):
                    logger.debug(
                        f"increment detected is '{new_increment}' due to '{found_keyword}' in '{message}'"
                    )
                    increment = new_increment

                if increment == MAJOR:
                    break

    return cast(Increment, increment)


def update_version_in_files(
    current_version: str,
    new_version: str,
    files: list[str],
    *,
    check_consistency: bool = False,
    encoding: str = encoding,
) -> list[str]:
    """Change old version to the new one in every file given.

    Note that this version is not the tag formatted one.
    So for example, your tag could look like `v1.0.0` while your version in
    the package like `1.0.0`.

    Returns the list of updated files.
    """
    # TODO: separate check step and write step
    updated = []
    for path, regex in files_and_regexs(files, current_version):
        current_version_found, version_file = _bump_with_regex(
            path,
            current_version,
            new_version,
            regex,
            encoding=encoding,
        )

        if check_consistency and not current_version_found:
            raise CurrentVersionNotFoundError(
                f"Current version {current_version} is not found in {path}.\n"
                "The version defined in commitizen configuration and the ones in "
                "version_files are possibly inconsistent."
            )

        # Write the file out again
        with smart_open(path, "w", encoding=encoding) as file:
            file.write(version_file)
        updated.append(path)
    return updated


def files_and_regexs(patterns: list[str], version: str) -> list[tuple[str, str]]:
    """
    Resolve all distinct files with their regexp from a list of glob patterns with optional regexp
    """
    out = []
    for pattern in patterns:
        drive, tail = os.path.splitdrive(pattern)
        path, _, regex = tail.partition(":")
        filepath = drive + path
        if not regex:
            regex = _version_to_regex(version)

        for path in iglob(filepath):
            out.append((path, regex))
    return sorted(list(set(out)))


def _bump_with_regex(
    version_filepath: str,
    current_version: str,
    new_version: str,
    regex: str,
    encoding: str = encoding,
) -> tuple[bool, str]:
    current_version_found = False
    lines = []
    pattern = re.compile(regex)
    with open(version_filepath, encoding=encoding) as f:
        for line in f:
            if pattern.search(line):
                bumped_line = line.replace(current_version, new_version)
                if bumped_line != line:
                    current_version_found = True
                lines.append(bumped_line)
            else:
                lines.append(line)
    return current_version_found, "".join(lines)


def _version_to_regex(version: str) -> str:
    return version.replace(".", r"\.").replace("+", r"\+")


def create_commit_message(
    current_version: Version | str,
    new_version: Version | str,
    message_template: str | None = None,
) -> str:
    if message_template is None:
        message_template = bump_message
    t = Template(message_template)
    return t.safe_substitute(current_version=current_version, new_version=new_version)
