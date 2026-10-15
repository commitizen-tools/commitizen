from __future__ import annotations

import os
import re
from glob import iglob
from string import Template
from typing import TYPE_CHECKING

from commitizen.defaults import BUMP_MESSAGE
from commitizen.exceptions import CurrentVersionNotFoundError
from commitizen.git import smart_open

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable

    from commitizen.version_schemes import VersionProtocol


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
        inconsistent_lines: list[tuple[int, str]] = []
        bumped_lines = []

        with open(path, encoding=encoding) as version_file:
            for lineno, line in enumerate(version_file, 1):
                if pattern.search(line):
                    if current_version in line:
                        bumped_line = line.replace(current_version, new_version)
                        current_version_found = True
                    else:
                        # The version-files regex matched this line, but the
                        # current version isn't on it. If the line looks like
                        # it sets a version-shaped value, this is almost
                        # certainly an inconsistent source we'd otherwise miss
                        # silently (#595).
                        bumped_line = line
                        if check_consistency and _LIKELY_VERSION_VALUE_RE.search(line):
                            inconsistent_lines.append((lineno, line.rstrip("\r\n")))
                else:
                    bumped_line = line

                bumped_lines.append(bumped_line)

        if check_consistency and not current_version_found:
            raise CurrentVersionNotFoundError(
                f"Current version {current_version} is not found in {path}.\n"
                "The version defined in commitizen configuration and the ones in "
                "version_files are possibly inconsistent."
            )

        if check_consistency and inconsistent_lines:
            details = "\n".join(f"  line {n}: {text}" for n, text in inconsistent_lines)
            raise CurrentVersionNotFoundError(
                f"Found line(s) in {path} matching the version regex but "
                f"holding a version other than {current_version}:\n"
                f"{details}\n"
                "This usually means another tool (e.g. poetry, pep621) is "
                "tracking a different version. Either align them, narrow the "
                "`version_files` regex, or drop `--check-consistency`."
            )

        bumped_version_file_content = "".join(bumped_lines)

        # Write the file out again
        with smart_open(path, "w", encoding=encoding) as file:
            file.write(bumped_version_file_content)
        updated_files.append(path)

    return updated_files


# Lines that look like ``key = "1.2.3"`` / ``key: 1.2.3-rc.0`` etc. -- enough
# to catch the typical pyproject.toml ``[tool.poetry].version = "..."`` and
# ``[project].version = "..."`` cases handled by ``--check-consistency``.
_LIKELY_VERSION_VALUE_RE = re.compile(r"\d+\.\d+\.\d+(?:[\w.\-+]*)")


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
