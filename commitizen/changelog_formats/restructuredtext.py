from __future__ import annotations

import sys
from itertools import zip_longest
from typing import IO, TYPE_CHECKING, Any, Union

from commitizen.changelog import Metadata

from .base import BaseFormat

if TYPE_CHECKING:
    # TypeAlias is Python 3.10+ but backported in typing-extensions
    if sys.version_info >= (3, 10):
        from typing import TypeAlias
    else:
        from typing_extensions import TypeAlias


# Can't use `|` operator and native type because of https://bugs.python.org/issue42233 only fixed in 3.10
TitleKind: TypeAlias = Union[str, tuple[str, str]]


class RestructuredText(BaseFormat):
    extension = "rst"

    def get_metadata_from_file(self, file: IO[Any]) -> Metadata:
        """
        RestructuredText section titles are not one-line-based,
        they spread on 2 or 3 lines and levels are not predefined
        but determined byt their occurrence order.

        It requires its own algorithm.

        For a more generic approach, you need to rely on `docutils`.
        """
        meta = Metadata()
        unreleased_title_kind: TitleKind | None = None
        in_overlined_title = False
        lines = file.readlines()
        for index, (first, second, third) in enumerate(
            zip_longest(lines, lines[1:], lines[2:], fillvalue="")
        ):
            first = first.strip().lower()
            second = second.strip().lower()
            third = third.strip().lower()
            title: str | None = None
            kind: TitleKind | None = None
            if self.is_overlined_title(first, second, third):
                title = second
                kind = (first[0], third[0])
                in_overlined_title = True
            elif not in_overlined_title and self.is_underlined_title(first, second):
                title = first
                kind = second[0]
            else:
                in_overlined_title = False

            if title:
                if "unreleased" in title:
                    unreleased_title_kind = kind
                    meta.unreleased_start = index
                    continue
                elif unreleased_title_kind and unreleased_title_kind == kind:
                    meta.unreleased_end = index
                # Try to find the latest release done
                if version := self.tag_rules.search_version(title):
                    meta.latest_version = version[0]
                    meta.latest_version_tag = version[1]
                    meta.latest_version_position = index
                    break
        if meta.unreleased_start is not None and meta.unreleased_end is None:
            meta.unreleased_end = (
                meta.latest_version_position if meta.latest_version else index + 1
            )

        return meta

    def is_overlined_title(self, first: str, second: str, third: str) -> bool:
        return (
            len(first) >= len(second)
            and len(first) == len(third)
            and all(char == first[0] for char in first[1:])
            and first[0] == third[0]
            and self.is_underlined_title(second, third)
        )

    def is_underlined_title(self, first: str, second: str) -> bool:
        return (
            len(second) >= len(first)
            and not second.isalnum()
            and all(char == second[0] for char in second[1:])
        )
