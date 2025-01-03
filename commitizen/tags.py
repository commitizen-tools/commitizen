from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from functools import cached_property
from string import Template
from typing import TYPE_CHECKING

from typing_extensions import Self

from commitizen import out
from commitizen.defaults import DEFAULT_SETTINGS, Settings, get_tag_regexes
from commitizen.git import GitTag
from commitizen.version_schemes import (
    DEFAULT_SCHEME,
    InvalidVersion,
    Version,
    VersionScheme,
    get_version_scheme,
)

if TYPE_CHECKING:
    from commitizen.version_schemes import VersionScheme


@dataclass
class TagRules:
    """
    Encapsulate tag-related rules
    """

    scheme: VersionScheme = DEFAULT_SCHEME
    tag_format: str = DEFAULT_SETTINGS["tag_format"]
    legacy_tag_formats: Sequence[str] = field(default_factory=list)
    ignored_tag_formats: Sequence[str] = field(default_factory=list)
    merge_prereleases: bool = False

    @cached_property
    def version_regexes(self) -> Sequence[re.Pattern]:
        tag_formats = [self.tag_format, *self.legacy_tag_formats]
        regexes = (self._format_regex(p) for p in tag_formats)
        return [re.compile(r) for r in regexes]

    @cached_property
    def ignored_regexes(self) -> Sequence[re.Pattern]:
        regexes = (self._format_regex(p, star=True) for p in self.ignored_tag_formats)
        return [re.compile(r) for r in regexes]

    def _format_regex(self, tag_pattern: str, star: bool = False) -> str:
        tag_regexes = get_tag_regexes(self.scheme.parser.pattern)
        format_regex = tag_pattern.replace("*", "(?:.*?)") if star else tag_pattern
        for pattern, regex in tag_regexes.items():
            format_regex = format_regex.replace(pattern, regex)
        return format_regex

    def is_version_tag(self, tag: str | GitTag) -> bool:
        """True if a given tag is a legit version tag"""
        tag = tag.name if isinstance(tag, GitTag) else tag
        return any(regex.match(tag) for regex in self.version_regexes)

    def is_ignored_tag(self, tag: str | GitTag) -> bool:
        """True if a given tag can be ignored"""
        tag = tag.name if isinstance(tag, GitTag) else tag
        return any(regex.match(tag) for regex in self.ignored_regexes)

    def _select_tag(self, tag: GitTag, warn: bool = False) -> bool:
        if self.is_version_tag(tag.name):
            return True
        if warn and not self.is_ignored_tag(tag.name):
            out.warn(
                f"InvalidVersion {tag.name} doesn't match any configured tag format"
            )
        return False

    def get_version_tags(
        self, tags: Sequence[GitTag], warn: bool = False
    ) -> Sequence[GitTag]:
        """Filter in version tags and warn on unexpected tags"""
        return [tag for tag in tags if self._select_tag(tag, warn)]

    def extract_version(self, tag: GitTag) -> Version:
        candidates = (
            match
            for regex in self.version_regexes
            if (match := regex.fullmatch(tag.name))
        )
        if not (m := next(candidates, None)):
            raise InvalidVersion()
        version = self._version_string(m)
        return self.scheme(version)

    def _version_string(self, match: re.Match[str]) -> str:
        if "version" in match.groupdict():
            return match.group("version")

        parts = match.groupdict()
        version = parts["major"]

        if minor := parts.get("minor"):
            version = f"{version}.{minor}"
        if patch := parts.get("patch"):
            version = f"{version}.{patch}"

        if parts.get("prerelease"):
            version = f"{version}-{parts['prerelease']}"
        if parts.get("devrelease"):
            version = f"{version}{parts['devrelease']}"

        return version

    def include_in_changelog(self, tag: GitTag) -> bool:
        """Check if a tag should be included in the changelog"""
        try:
            version = self.extract_version(tag)
        except InvalidVersion:
            return False

        if self.merge_prereleases and version.is_prerelease:
            return False

        return True

    def search_version(self, txt: str, last: bool = False) -> tuple[str, str] | None:
        """
        Search the first or last version tag occurrence in txt.

        Returns a 2-tuple (version, version_tag) if found
        """
        candidates = (
            m for regex in self.version_regexes if len(m := list(regex.finditer(txt)))
        )
        if not (matches := next(candidates, [])):
            return None

        match = matches[-1 if last else 0]

        if "version" in match.groupdict():
            return match.group("version"), match.group(0)

        parts = match.groupdict()
        try:
            version = f"{parts['major']}.{parts['minor']}.{parts['patch']}"
        except KeyError:
            return None

        if parts.get("prerelease"):
            version = f"{version}-{parts['prerelease']}"
        if parts.get("devrelease"):
            version = f"{version}{parts['devrelease']}"
        return version, match.group(0)

    def normalize_tag(
        self, version: Version | str, tag_format: str | None = None
    ) -> str:
        """The tag and the software version might be different.

        That's why this function exists.

        Example:
        | tag | version (PEP 0440) |
        | --- | ------- |
        | v0.9.0 | 0.9.0 |
        | ver1.0.0 | 1.0.0 |
        | ver1.0.0.a0 | 1.0.0a0 |
        """
        version = self.scheme(version) if isinstance(version, str) else version
        tag_format = tag_format or self.tag_format

        major, minor, patch = version.release
        prerelease = version.prerelease or ""

        t = Template(tag_format)
        return t.safe_substitute(
            version=version,
            major=major,
            minor=minor,
            patch=patch,
            prerelease=prerelease,
        )

    def find_tag_for(
        self, tags: Sequence[GitTag], version: Version | str
    ) -> GitTag | None:
        version = self.scheme(version) if isinstance(version, str) else version
        possible_tags = [
            self.normalize_tag(version, f)
            for f in (self.tag_format, *self.legacy_tag_formats)
        ]
        candidates = (t for t in tags if any(t.name == p for p in possible_tags))
        return next(candidates, None)

    @classmethod
    def from_settings(cls, settings: Settings) -> Self:
        return cls(
            scheme=get_version_scheme(settings),
            tag_format=settings["tag_format"],
            legacy_tag_formats=settings["legacy_tag_formats"],
            ignored_tag_formats=settings["ignored_tag_formats"],
            merge_prereleases=settings["changelog_merge_prerelease"],
        )
