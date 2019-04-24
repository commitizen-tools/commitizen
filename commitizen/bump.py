import re
from collections import defaultdict
from itertools import zip_longest
from string import Template
from packaging.version import Version
from typing import List, Optional, Union
from commitizen.defaults import (
    MAJOR,
    MINOR,
    PATCH,
    bump_pattern,
    bump_map,
    bump_message,
)


def find_increment(
    messages: List[str], regex: str = bump_pattern, increments_map: dict = bump_map
) -> Optional[str]:

    # Most important cases are major and minor.
    # Everything else will be considered patch.
    increments_map_default = defaultdict(lambda: None, increments_map)
    pattern = re.compile(regex)
    increment = None

    for message in messages:
        result = pattern.search(message)
        if not result:
            continue
        found_keyword = result.group(0)
        new_increment = increments_map_default[found_keyword]
        if new_increment == "MAJOR":
            increment = new_increment
            break
        elif increment == "MINOR" and new_increment == "PATCH":
            continue
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
    new_prerelease_number: int = 0
    if version.is_prerelease and prerelease.startswith(version.pre[0]):
        prev_prerelease: int = list(version.pre)[1]
        new_prerelease_number = prev_prerelease + 1
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
    for filepath in files:
        # Read in the file
        with open(filepath, "r") as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace(current_version, new_version)

        # Write the file out again
        with open(filepath, "w") as file:
            file.write(filedata)


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
    if version.is_prerelease:
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
