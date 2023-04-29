from __future__ import annotations

import re

from .base import BaseFormat


class Textile(BaseFormat):
    extension = "textile"

    RE_TITLE = re.compile(r"^h(?P<level>\d)\. (?P<title>.*)$")

    def parse_version_from_title(self, line: str) -> str | None:
        if not self.RE_TITLE.match(line):
            return None
        m = re.search(self.version_parser, line)
        if not m:
            return None
        return m.group("version")

    def parse_title_level(self, line: str) -> int | None:
        m = self.RE_TITLE.match(line)
        if not m:
            return None
        return int(m.group("level"))
