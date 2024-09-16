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
        if "version" in m.groupdict():
            return m.group("version")
        matches = m.groupdict()
        try:
            partial_version = (
                f"{matches['major']}.{matches['minor']}.{matches['patch']}"
            )
        except KeyError:
            return None

        if matches.get("prerelease"):
            partial_version += f"-{matches['prerelease']}"
        if matches.get("devrelease"):
            partial_version += f"{matches['devrelease']}"
        return partial_version

    def parse_title_level(self, line: str) -> int | None:
        m = self.RE_TITLE.match(line)
        if not m:
            return None
        return int(m.group("level"))
