import re
from collections import OrderedDict
from itertools import zip_longest
from string import Template
from typing import List, Optional, Union

from packaging.version import Version

from commitizen.defaults import (
    MAJOR,
    MINOR,
    PATCH,
    bump_map,
    bump_message,
    bump_pattern,
)
from commitizen.git import GitCommit


def find_increment(
    commits: List[GitCommit],
    regex: str = bump_pattern,
    increments_map: Union[dict, OrderedDict] = bump_map,
) -> Optional[str]:

    if isinstance(increments_map, dict):
        increments_map = OrderedDict(increments_map)

    # Most important cases are major and minor.
    # Everything else will be considered patch.
    select_pattern = re.compile(regex)
    increment = None

    for commit in commits:
        for message in commit.message.split("\n"):
            result = select_pattern.search(message)
            if result:
                found_keyword = result.group(0)
                new_increment = None
                for match_pattern in increments_map.keys():
                    if re.match(match_pattern, found_keyword):
                        new_increment = increments_map[match_pattern]
                        break

                if increment == "MAJOR":
                    continue
                elif increment == "MINOR" and new_increment == "MAJOR":
                    increment = new_increment
                elif increment == "PATCH" or increment is None:
                    increment = new_increment

    return increment


def prerelease_generator(current_version: str, prerelease: Optional[str] = None) -> str:
    """
    X.YaN   # Alpha release
    X.YbN   # Beta release
    X.YrcN  # Release Candidate
    X.Y  # Final

    This function might return something like 'alpha1'
    but it will be handled by Version.
    """
    if not prerelease:
        return ""

    version = Version(current_version)
    # version.pre is needed for mypy check
    if version.is_prerelease and version.pre and prerelease.startswith(version.pre[0]):
        prev_prerelease: int = version.pre[1]
        new_prerelease_number = prev_prerelease + 1
    else:
        new_prerelease_number = 0
    pre_version = f"{prerelease}{new_prerelease_number}"
    return pre_version


def semver_generator(current_version: str, increment: str = None) -> str:
    version = Version(current_version)
    prev_release = list(version.release)
    increments = [MAJOR, MINOR, PATCH]
    increments_version = dict(zip_longest(increments, prev_release, fillvalue=0))

    # This flag means that current version
    # must remove its prerelease tag,
    # so it doesn't matter the increment.
    # Example: 1.0.0a0 with PATCH/MINOR -> 1.0.0
    if not version.is_prerelease:

        if increment == MAJOR:
            increments_version[MAJOR] += 1
            increments_version[MINOR] = 0
            increments_version[PATCH] = 0
        elif increment == MINOR:
            increments_version[MINOR] += 1
            increments_version[PATCH] = 0
        elif increment == PATCH:
            increments_version[PATCH] += 1

    return str(
        f"{increments_version['MAJOR']}."
        f"{increments_version['MINOR']}."
        f"{increments_version['PATCH']}"
    )


def generate_version(
    current_version: str, increment: str, prerelease: Optional[str] = None
) -> Version:
    """Based on the given increment a proper semver will be generated.

    For now the rules and versioning scheme is based on
    python's PEP 0440.
    More info: https://www.python.org/dev/peps/pep-0440/

    Example:
        PATCH 1.0.0 -> 1.0.1
        MINOR 1.0.0 -> 1.1.0
        MAJOR 1.0.0 -> 2.0.0
    """
    pre_version = prerelease_generator(current_version, prerelease=prerelease)
    semver = semver_generator(current_version, increment=increment)
    # TODO: post version
    # TODO: dev version
    return Version(f"{semver}{pre_version}")


def update_version_in_files(current_version: str, new_version: str, files: list):
    """Change old version to the new one in every file given.

    Note that this version is not the tag formatted one.
    So for example, your tag could look like `v1.0.0` while your version in
    the package like `1.0.0`.
    """
    for location in files:
        filepath, *regex = location.split(":", maxsplit=1)
        if len(regex) > 0:
            regex = regex[0]

        # Read in the file
        filedata = []
        with open(filepath, "r") as f:
            for line in f:
                if regex:
                    is_match = re.search(regex, line)
                    if not is_match:
                        filedata.append(line)
                        continue

                # Replace the target string
                filedata.append(line.replace(current_version, new_version))

        # Write the file out again
        with open(filepath, "w") as file:
            file.write("".join(filedata))


def create_tag(version: Union[Version, str], tag_format: Optional[str] = None):
    """The tag and the software version might be different.

    That's why this function exists.

    Example:

    | tag | version (PEP 0440) |
    | --- | ------- |
    | v0.9.0 | 0.9.0 |
    | ver1.0.0 | 1.0.0 |
    | ver1.0.0.a0 | 1.0.0a0 |

    """
    if isinstance(version, str):
        version = Version(version)

    if not tag_format:
        return version.public

    major, minor, patch = version.release
    prerelease = ""
    # version.pre is needed for mypy check
    if version.is_prerelease and version.pre:
        prerelease = f"{version.pre[0]}{version.pre[1]}"

    t = Template(tag_format)
    return t.safe_substitute(
        version=version, major=major, minor=minor, patch=patch, prerelease=prerelease
    )


def create_commit_message(
    current_version: Union[Version, str],
    new_version: Union[Version, str],
    message_template: str = None,
) -> str:
    if message_template is None:
        message_template = bump_message
    t = Template(message_template)
    return t.safe_substitute(current_version=current_version, new_version=new_version)
