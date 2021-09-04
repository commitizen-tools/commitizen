import re
from collections import OrderedDict
from datetime import datetime
from itertools import zip_longest
from string import Template
from typing import Iterable, List, Optional, Tuple, Union

from packaging.version import Version

from commitizen.defaults import (
    MAJOR,
    MINOR,
    PATCH,
    bump_map,
    bump_message,
    bump_pattern,
)
from commitizen.exceptions import CurrentVersionNotFoundError
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


# TODO: Create new Version class to parse the version based on tag_format and encapsulate the bump logic
def _parse_release_semver(
    release: Iterable[int], tag_format: Optional[str] = None
) -> Tuple[int, int, int]:
    """Parse the SemVer components from the release version by handling reordering and CalVer."""
    major, minor, patch = [*release, 0, 0, 0][:3]
    if tag_format:
        semver_names = ["major", "minor", "patch"]
        tag_format = tag_format.replace("$version", "$" + ".$".join(semver_names))
        keys = [key.split("$")[-1] for key in tag_format.split(".")]
        if len(keys) == len(list(release)) and any(key in keys for key in semver_names):
            tag_lookup = dict(zip(keys, release))
            major, minor, patch = [tag_lookup.get(key, 0) for key in semver_names]

    return major, minor, patch


def _merge_semver(
    _current: str, _new_semver: str, tag_format: Optional[str] = None
) -> str:
    """HACK: Merge the results of the incremented SemVer back into the release version to handle CalVer."""
    current: Iterable[int] = Version(_current).release
    new_semver: Iterable[int] = Version(_new_semver).release

    release = new_semver
    if tag_format:
        semver_names = ["major", "minor", "patch"]
        semver_lookup = dict(zip(semver_names, new_semver))
        tag_format = tag_format.replace("$version", "$" + ".$".join(semver_names))
        keys = [key.split("$")[-1] for key in tag_format.split(".")]
        if len(keys) == len(list(current)):
            release = [
                semver_lookup.get(key, value) for key, value in zip(keys, current)
            ]

    return ".".join(map(str, release))


def prerelease_generator(current_version: str, prerelease: Optional[str] = None) -> str:
    """Generate prerelease

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


def semver_generator(
    current_version: str, increment: str = None, tag_format: Optional[str] = None
) -> str:
    version = Version(current_version)
    prev_release = list(_parse_release_semver(version.release, tag_format))
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
    current_version: str,
    increment: str,
    prerelease: Optional[str] = None,
    is_local_version: bool = False,
    tag_format: Optional[str] = None,
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
    if is_local_version:
        version = Version(current_version)
        pre_version = prerelease_generator(str(version.local), prerelease=prerelease)
        semver = semver_generator(
            str(version.local), increment=increment, tag_format=tag_format
        )

        return Version(f"{version.public}+{semver}{pre_version}")
    else:
        pre_version = prerelease_generator(current_version, prerelease=prerelease)
        semver = semver_generator(
            current_version, increment=increment, tag_format=tag_format
        )
        release = _merge_semver(current_version, semver, tag_format)

        # TODO: post version
        # TODO: dev version
        return Version(f"{release}{pre_version}")


def update_version_in_files(
    current_version: str, new_version: str, files: List[str], *, check_consistency=False
):
    """Change old version to the new one in every file given.

    Note that this version is not the tag formatted one.
    So for example, your tag could look like `v1.0.0` while your version in
    the package like `1.0.0`.
    """
    # TODO: separate check step and write step
    for location in files:
        filepath, *regexes = location.split(":")
        regex = regexes[0] if regexes else None

        with open(filepath, "r") as f:
            version_file = f.read()

        if regex:
            current_version_found, version_file = _bump_with_regex(
                version_file, current_version, new_version, regex
            )
        else:
            current_version_regex = _version_to_regex(current_version)
            current_version_found = bool(current_version_regex.search(version_file))
            version_file = current_version_regex.sub(new_version, version_file)

        if check_consistency and not current_version_found:
            raise CurrentVersionNotFoundError(
                f"Current version {current_version} is not found in {location}.\n"
                "The version defined in commitizen configuration and the ones in "
                "version_files are possibly inconsistent."
            )

        # Write the file out again
        with open(filepath, "w") as file:
            file.write("".join(version_file))


def _bump_with_regex(version_file_contents, current_version, new_version, regex):
    current_version_found = False
    # Bumping versions that change the string length move the offset on the file contents as finditer keeps a
    # reference to the initial string that was used and calling search many times would lead in infinite loops
    # e.g.: 1.1.9 -> 1.1.20
    offset = 0
    for match in re.finditer(regex, version_file_contents, re.MULTILINE):
        left = version_file_contents[: match.end() + offset]
        right = version_file_contents[match.end() + offset :]

        line_break = right.find("\n")
        middle = right[:line_break]
        right = right[line_break:]

        if current_version in middle:
            offset += len(new_version) - len(current_version)
            current_version_found = True
            version_file_contents = (
                left + middle.replace(current_version, new_version) + right
            )
    return current_version_found, version_file_contents


def _version_to_regex(version: str):
    clean_regex = version.replace(".", r"\.").replace("+", r"\+")
    return re.compile(f"{clean_regex}")


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
        return str(version)

    major, minor, patch = _parse_release_semver(version.release, tag_format)
    prerelease = ""
    # version.pre is needed for mypy check
    if version.is_prerelease and version.pre:
        prerelease = f"{version.pre[0]}{version.pre[1]}"

    t = Template(tag_format)
    t_ver = t.safe_substitute(
        version=version, major=major, minor=minor, patch=patch, prerelease=prerelease
    )
    return datetime.utcnow().strftime(t_ver)


def create_commit_message(
    current_version: Union[Version, str],
    new_version: Union[Version, str],
    message_template: str = None,
) -> str:
    if message_template is None:
        message_template = bump_message
    t = Template(message_template)
    return t.safe_substitute(current_version=current_version, new_version=new_version)
