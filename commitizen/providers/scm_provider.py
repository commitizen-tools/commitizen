from __future__ import annotations

import re
from typing import Callable


from commitizen.git import get_tags
from commitizen.version_schemes import (
    get_version_scheme,
    InvalidVersion,
    Version,
    VersionProtocol,
)

from commitizen.providers.base_provider import VersionProvider


class ScmProvider(VersionProvider):
    """
    A provider fetching the current/last version from the repository history

    The version is fetched using `git describe` and is never set.

    It is meant for `setuptools-scm` or any package manager `*-scm` provider.
    """

    TAG_FORMAT_REGEXS = {
        "$version": r"(?P<version>.+)",
        "$major": r"(?P<major>\d+)",
        "$minor": r"(?P<minor>\d+)",
        "$patch": r"(?P<patch>\d+)",
        "$prerelease": r"(?P<prerelease>\w+\d+)?",
        "$devrelease": r"(?P<devrelease>\.dev\d+)?",
    }

    def _tag_format_matcher(self) -> Callable[[str], VersionProtocol | None]:
        version_scheme = get_version_scheme(self.config)
        pattern = self.config.settings["tag_format"]
        if pattern == "$version":
            pattern = version_scheme.parser.pattern
        for var, tag_pattern in self.TAG_FORMAT_REGEXS.items():
            pattern = pattern.replace(var, tag_pattern)

        regex = re.compile(f"^{pattern}$", re.VERBOSE)

        def matcher(tag: str) -> Version | None:
            match = regex.match(tag)
            if not match:
                return None
            groups = match.groupdict()
            if "version" in groups:
                ver = groups["version"]
            elif "major" in groups:
                ver = "".join(
                    (
                        groups["major"],
                        f".{groups['minor']}" if groups.get("minor") else "",
                        f".{groups['patch']}" if groups.get("patch") else "",
                        groups["prerelease"] if groups.get("prerelease") else "",
                        groups["devrelease"] if groups.get("devrelease") else "",
                    )
                )
            elif pattern == version_scheme.parser.pattern:
                ver = tag
            else:
                return None

            try:
                return version_scheme(ver)
            except InvalidVersion:
                return None

        return matcher

    def get_version(self) -> str:
        matcher = self._tag_format_matcher()
        matches = sorted(
            version
            for t in get_tags(reachable_only=True)
            if (version := matcher(t.name))
        )
        if not matches:
            return "0.0.0"
        return str(matches[-1])

    def set_version(self, version: str):
        # Not necessary
        pass
