from __future__ import annotations

import re

from .base import BaseFormat


class AsciiDoc(BaseFormat):
    extension = "adoc"

    RE_TITLE = re.compile(r"^(?P<level>=+) (?P<title>.*)$")

    def parse_version_from_title(self, line: str) -> str | None:
        m = self.RE_TITLE.match(line)
        if not m:
            return None
        # Capture last match as AsciiDoc use postfixed URL labels
        matches = list(re.finditer(self.version_parser, m.group("title")))
        if not matches:
            return None
        if "version" in matches[-1].groupdict():
            return matches[-1].group("version")
        partial_matches = matches[-1].groupdict()
        try:
            partial_version = f"{partial_matches['major']}.{partial_matches['minor']}.{partial_matches['patch']}"
        except KeyError:
            return None

        if partial_matches.get("prerelease"):
            partial_version = f"{partial_version}-{partial_matches['prerelease']}"
        if partial_matches.get("devrelease"):
            partial_version = f"{partial_version}{partial_matches['devrelease']}"
        return partial_version

    def parse_title_level(self, line: str) -> int | None:
        m = self.RE_TITLE.match(line)
        if not m:
            return None
        return len(m.group("level"))
