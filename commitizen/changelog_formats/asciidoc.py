from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .base import BaseFormat

if TYPE_CHECKING:
    from commitizen.tags import VersionTag


class AsciiDoc(BaseFormat):
    extension = "adoc"

    RE_TITLE = re.compile(r"^(?P<level>=+) (?P<title>.*)$")

    def parse_version_from_title(self, line: str) -> VersionTag | None:
        m = self.RE_TITLE.match(line)
        if not m:
            return None
        # Capture last match as AsciiDoc use postfixed URL labels
        return self.tag_rules.search_version(m.group("title"), last=True)

    def parse_title_level(self, line: str) -> int | None:
        m = self.RE_TITLE.match(line)
        if not m:
            return None
        return len(m.group("level"))
