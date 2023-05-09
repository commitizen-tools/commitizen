from __future__ import annotations

import re

from typing import Optional

from commitizen import defaults

from .base import BaseFormat


class Textile(BaseFormat):
    extension = "textile"

    RE_TITLE = re.compile(r"^h(?P<level>\d)\. (?P<title>.*)$")

    def parse_version_from_title(self, line: str) -> Optional[str]:
        if not self.RE_TITLE.match(line):
            return None
        m = re.search(defaults.version_parser, line)
        if not m:
            return None
        return m.group("version")

    def parse_title_level(self, line: str) -> Optional[int]:
        m = self.RE_TITLE.match(line)
        if not m:
            return None
        return int(m.group("level"))
