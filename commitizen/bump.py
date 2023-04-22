from __future__ import annotations

import os
import re
from collections import OrderedDict
from string import Template

from commitizen.defaults import bump_message
from commitizen.exceptions import CurrentVersionNotFoundError
from commitizen.git import GitCommit, smart_open
from commitizen.version_schemes import DEFAULT_SCHEME, VersionScheme, Version


def find_increment(
    commits: list[GitCommit], regex: str, increments_map: dict | OrderedDict
) -> str | None:
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

                if increment == "MAJOR":
                    break
                elif increment == "MINOR" and new_increment == "MAJOR":
                    increment = new_increment
                elif increment == "PATCH" or increment is None:
                    increment = new_increment

    return increment


def update_version_in_files(
    current_version: str, new_version: str, files: list[str], *, check_consistency=False
) -> None:
    """Change old version to the new one in every file given.

    Note that this version is not the tag formatted one.
    So for example, your tag could look like `v1.0.0` while your version in
    the package like `1.0.0`.
    """
    # TODO: separate check step and write step
    for location in files:
        drive, tail = os.path.splitdrive(location)
        path, _, regex = tail.partition(":")
        filepath = drive + path
        if not regex:
            regex = _version_to_regex(current_version)

        current_version_found, version_file = _bump_with_regex(
            filepath, current_version, new_version, regex
        )

        if check_consistency and not current_version_found:
            raise CurrentVersionNotFoundError(
                f"Current version {current_version} is not found in {location}.\n"
                "The version defined in commitizen configuration and the ones in "
                "version_files are possibly inconsistent."
            )

        # Write the file out again
        with smart_open(filepath, "w") as file:
            file.write(version_file)


def _bump_with_regex(
    version_filepath: str, current_version: str, new_version: str, regex: str
) -> tuple[bool, str]:
    current_version_found = False
    lines = []
    pattern = re.compile(regex)
    with open(version_filepath, "r") as f:
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


def normalize_tag(
    version: Version | str,
    tag_format: str | None = None,
    scheme: VersionScheme | None = None,
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
    scheme = scheme or DEFAULT_SCHEME
    version = scheme(version) if isinstance(version, str) else version

    if not tag_format:
        return str(version)

    major, minor, patch = version.release
    prerelease = version.prerelease or ""

    t = Template(tag_format)
    return t.safe_substitute(
        version=version, major=major, minor=minor, patch=patch, prerelease=prerelease
    )


def create_commit_message(
    current_version: Version | str,
    new_version: Version | str,
    message_template: str | None = None,
) -> str:
    if message_template is None:
        message_template = bump_message
    t = Template(message_template)
    return t.safe_substitute(current_version=current_version, new_version=new_version)
