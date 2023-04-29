from __future__ import annotations

import re

from .base import BaseFormat


class Markdown(BaseFormat):
    extension = "md"

    alternative_extensions = {"markdown", "mkd"}

    RE_TITLE = re.compile(r"^(?P<level>#+) (?P<title>.*)$")

    def parse_version_from_title(self, line: str) -> str | None:
        m = self.RE_TITLE.match(line)
        if not m:
            return None
        m = re.search(self.version_parser, m.group("title"))
        if not m:
            return None
        return m.group("version")

    def parse_title_level(self, line: str) -> int | None:
        m = self.RE_TITLE.match(line)
        if not m:
            return None
        return len(m.group("level"))
