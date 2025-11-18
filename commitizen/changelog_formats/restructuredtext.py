from __future__ import annotations

from itertools import zip_longest
from typing import IO

from commitizen.changelog import Metadata

from .base import BaseFormat


class RestructuredText(BaseFormat):
    extension = "rst"

    def get_metadata_from_file(self, file: IO[str]) -> Metadata:
        """
        RestructuredText section titles are not one-line-based,
        they spread on 2 or 3 lines and levels are not predefined
        but determined by their occurrence order.

        It requires its own algorithm.

        For a more generic approach, you need to rely on `docutils`.
        """
        out_metadata = Metadata()
        unreleased_title_kind: str | tuple[str, str] | None = None
        is_overlined_title = False
        lines = [line.strip().lower() for line in file.readlines()]

        for index, (first, second, third) in enumerate(
            zip_longest(lines, lines[1:], lines[2:], fillvalue="")
        ):
            title: str | None = None
            kind: str | tuple[str, str] | None = None
            if _is_overlined_title(first, second, third):
                title = second
                kind = (first[0], third[0])
                is_overlined_title = True
            elif not is_overlined_title and _is_underlined_title(first, second):
                title = first
                kind = second[0]
            else:
                is_overlined_title = False

            if not title:
                continue

            if "unreleased" in title:
                unreleased_title_kind = kind
                out_metadata.unreleased_start = index
                continue

            if unreleased_title_kind and unreleased_title_kind == kind:
                out_metadata.unreleased_end = index
            # Try to find the latest release done
            if version := self.tag_rules.search_version(title):
                out_metadata.latest_version = version[0]
                out_metadata.latest_version_tag = version[1]
                out_metadata.latest_version_position = index
                break

        if (
            out_metadata.unreleased_start is not None
            and out_metadata.unreleased_end is None
        ):
            out_metadata.unreleased_end = (
                out_metadata.latest_version_position
                if out_metadata.latest_version
                else len(lines)
            )

        return out_metadata


def _is_overlined_title(first: str, second: str, third: str) -> bool:
    return (
        len(first) == len(third) >= len(second)
        and first[0] == third[0]
        and all(char == first[0] for char in first)
        and _is_underlined_title(second, third)
    )


def _is_underlined_title(first: str, second: str) -> bool:
    return (
        len(second) >= len(first)
        and not second.isalnum()
        and all(char == second[0] for char in second)
    )
