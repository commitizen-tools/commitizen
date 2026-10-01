from __future__ import annotations

import os
import re
from glob import iglob
from string import Template
from typing import TYPE_CHECKING, cast

from commitizen.defaults import BUMP_MESSAGE
from commitizen.exceptions import CurrentVersionNotFoundError
from commitizen.git import smart_open
from commitizen.version_increment import VersionIncrement

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable, Mapping

    from commitizen.git import GitCommit
    from commitizen.version_schemes import Increment, VersionProtocol


def find_increment(
    commits: list[GitCommit], regex: str, increments_map: Mapping[str, object]
) -> Increment | None:
    """Preserve the legacy bump helper as a compatibility shim.

    This public helper remains available for integrations importing
    ``commitizen.bump.find_increment`` while delegating the real increment
    comparison and extraction logic to ``VersionIncrement``.
    """
    increment = VersionIncrement.get_highest_by_messages(
        (commit.message for commit in commits),
        regex,
        increments_map,
    )
    if increment == VersionIncrement.NONE:
        return None
    return cast("Increment", str(increment))


def update_version_in_files(
    current_version: str,
    new_version: str,
    version_files: Iterable[str],
    *,
    check_consistency: bool,
    encoding: str,
) -> list[str]:
    """Change old version to the new one in every file given.

    Note that this version is not the tag formatted one.
    So for example, your tag could look like `v1.0.0` while your version in
    the package like `1.0.0`.

    Returns the list of updated files.
    """
    updated_files = []

    for path, pattern in _resolve_files_and_regexes(version_files, current_version):
        current_version_found = False
        bumped_lines = []

        with open(path, encoding=encoding) as version_file:
            for line in version_file:
                bumped_line = (
                    line.replace(current_version, new_version)
                    if pattern.search(line)
                    else line
                )

                current_version_found = current_version_found or bumped_line != line
                bumped_lines.append(bumped_line)

        if check_consistency and not current_version_found:
            raise CurrentVersionNotFoundError(
                f"Current version {current_version} is not found in {path}.\n"
                "The version defined in commitizen configuration and the ones in "
                "version_files are possibly inconsistent."
            )

        bumped_version_file_content = "".join(bumped_lines)

        # Write the file out again
        with smart_open(path, "w", encoding=encoding) as file:
            file.write(bumped_version_file_content)
        updated_files.append(path)

    return updated_files


def _resolve_files_and_regexes(
    patterns: Iterable[str], version: str
) -> Generator[tuple[str, re.Pattern], None, None]:
    """
    Resolve all distinct files with their regexp from a list of glob patterns with optional regexp
    """
    filepath_set: set[tuple[str, str]] = set()
    for pattern in patterns:
        drive, tail = os.path.splitdrive(pattern)
        path, _, regex = tail.partition(":")
        filepath = drive + path
        regex = regex or re.escape(version)

        filepath_set.update((path, regex) for path in iglob(filepath))

    return ((path, re.compile(regex)) for path, regex in sorted(filepath_set))


def create_commit_message(
    current_version: VersionProtocol | str,
    new_version: VersionProtocol | str,
    message_template: str | None = None,
) -> str:
    if message_template is None:
        message_template = BUMP_MESSAGE
    t = Template(message_template)
    return t.safe_substitute(current_version=current_version, new_version=new_version)
