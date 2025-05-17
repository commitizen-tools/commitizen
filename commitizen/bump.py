from __future__ import annotations

import os
import re
from collections.abc import Iterable
from glob import iglob
from string import Template

from commitizen.defaults import BUMP_MESSAGE, ENCODING
from commitizen.exceptions import CurrentVersionNotFoundError
from commitizen.git import smart_open
from commitizen.version_schemes import Version


def update_version_in_files(
    current_version: str,
    new_version: str,
    files: Iterable[str],
    *,
    check_consistency: bool = False,
    encoding: str = ENCODING,
) -> list[str]:
    """Change old version to the new one in every file given.

    Note that this version is not the tag formatted one.
    So for example, your tag could look like `v1.0.0` while your version in
    the package like `1.0.0`.

    Returns the list of updated files.
    """
    # TODO: separate check step and write step
    updated = []
    for path, regex in _files_and_regexes(files, current_version):
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


def _files_and_regexes(patterns: Iterable[str], version: str) -> list[tuple[str, str]]:
    """
    Resolve all distinct files with their regexp from a list of glob patterns with optional regexp
    """
    out: set[tuple[str, str]] = set()
    for pattern in patterns:
        drive, tail = os.path.splitdrive(pattern)
        path, _, regex = tail.partition(":")
        filepath = drive + path
        if not regex:
            regex = re.escape(version)

        for file in iglob(filepath):
            out.add((file, regex))

    return sorted(out)


def _bump_with_regex(
    version_filepath: str,
    current_version: str,
    new_version: str,
    regex: str,
    encoding: str = ENCODING,
) -> tuple[bool, str]:
    current_version_found = False
    lines = []
    pattern = re.compile(regex)
    with open(version_filepath, encoding=encoding) as f:
        for line in f:
            if not pattern.search(line):
                lines.append(line)
                continue

            bumped_line = line.replace(current_version, new_version)
            if bumped_line != line:
                current_version_found = True
            lines.append(bumped_line)

    return current_version_found, "".join(lines)


def create_commit_message(
    current_version: Version | str,
    new_version: Version | str,
    message_template: str | None = None,
) -> str:
    if message_template is None:
        message_template = BUMP_MESSAGE
    t = Template(message_template)
    return t.safe_substitute(current_version=current_version, new_version=new_version)
