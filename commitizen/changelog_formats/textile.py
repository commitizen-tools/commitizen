from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .base import BaseFormat

if TYPE_CHECKING:
    from commitizen.tags import VersionTag


class Textile(BaseFormat):
    extension = "textile"

    RE_TITLE = re.compile(r"^h(?P<level>\d)\. (?P<title>.*)$")

    def parse_version_from_title(self, line: str) -> VersionTag | None:
        if not self.RE_TITLE.match(line):
            return None
        return self.tag_rules.search_version(line)

    def parse_title_level(self, line: str) -> int | None:
        m = self.RE_TITLE.match(line)
        if not m:
            return None
        return int(m.group("level"))
