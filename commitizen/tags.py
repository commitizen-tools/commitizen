from __future__ import annotations

import re
import warnings
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from functools import cached_property
from itertools import chain
from string import Template
from typing import TYPE_CHECKING, NamedTuple

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
    import sys

    from commitizen.version_schemes import VersionScheme

    # Self is Python 3.11+ but backported in typing-extensions
    if sys.version_info < (3, 11):
        from typing_extensions import Self
    else:
        from typing import Self


class VersionTag(NamedTuple):
    """Represent a version and its matching tag form."""

    version: str
    tag: str


@dataclass
class TagRules:
    """
    Encapsulate tag-related rules.

    It allows to filter or match tags according to rules provided in settings:
    - `tag_format`: the current format of the tags generated on `bump`
    - `legacy_tag_formats`: previous known formats of the tag
    - `ignored_tag_formats`: known formats that should be ignored
    - `merge_prereleases`: if `True`, prereleases will be merged with their release counterpart
    - `version_scheme`: the version scheme to use, which will be used to parse and format versions

    This class is meant to abstract and centralize all the logic related to tags.
    To ensure consistency, it is recommended to use this class to handle tags.

    Example:

    ```python
    settings = DEFAULT_SETTINGS.clone()
    settings.update(
        {
            "tag_format": "v{version}",
            "legacy_tag_formats": ["version{version}", "ver{version}"],
            "ignored_tag_formats": ["ignored{version}"],
        }
    )

    rules = TagRules.from_settings(settings)

    assert rules.is_version_tag("v1.0.0")
    assert rules.is_version_tag("version1.0.0")
    assert rules.is_version_tag("ver1.0.0")
    assert not rules.is_version_tag("ignored1.0.0", warn=True)  # Does not warn
    assert not rules.is_version_tag("warn1.0.0", warn=True)  # Does warn

    assert rules.search_version("# My v1.0.0 version").version == "1.0.0"
    assert rules.extract_version("v1.0.0") == Version("1.0.0")
    try:
        assert rules.extract_version("not-a-v1.0.0")
    except InvalidVersion:
        print("Does not match a tag format")
    ```
    """

    scheme: VersionScheme = DEFAULT_SCHEME
    tag_format: str = DEFAULT_SETTINGS["tag_format"]
    legacy_tag_formats: Sequence[str] = field(default_factory=list)
    ignored_tag_formats: Sequence[str] = field(default_factory=list)
    merge_prereleases: bool = False

    @property
    def tag_formats(self) -> Iterable[str]:
        return chain([self.tag_format], self.legacy_tag_formats)

    @cached_property
    def version_regexes(self) -> list[re.Pattern]:
        """Regexes for all legit tag formats, current and legacy"""
        return [re.compile(self._format_regex(f)) for f in self.tag_formats]

    @cached_property
    def ignored_regexes(self) -> list[re.Pattern]:
        """Regexes for known but ignored tag formats"""
        return [
            re.compile(self._format_regex(f, star=True))
            for f in self.ignored_tag_formats
        ]

    def _format_regex(self, tag_pattern: str, star: bool = False) -> str:
        """
        Format a tag pattern into a regex pattern.

        If star is `True`, the `*` character will be considered as a wildcard.
        """
        tag_regexes = get_tag_regexes(self.scheme.parser.pattern)
        format_regex = tag_pattern.replace("*", "(?:.*?)") if star else tag_pattern
        for pattern, regex in tag_regexes.items():
            format_regex = format_regex.replace(pattern, regex)
        return format_regex

    def _version_tag_error(self, tag: str) -> str:
        """Format the error message for an invalid version tag"""
        return f"Invalid version tag: '{tag}' does not match any configured tag format"

    def is_version_tag(self, tag: str | GitTag, warn: bool = False) -> bool:
        """
        True if a given tag is a legit version tag.

        if `warn` is `True`, it will print a warning message if the tag is not a version tag.
        """
        tag = tag.name if isinstance(tag, GitTag) else tag
        is_legit = any(regex.fullmatch(tag) for regex in self.version_regexes)
        if warn and not is_legit and not self.is_ignored_tag(tag):
            out.warn(self._version_tag_error(tag))
        return is_legit

    def is_ignored_tag(self, tag: str | GitTag) -> bool:
        """True if a given tag can be ignored"""
        tag = tag.name if isinstance(tag, GitTag) else tag
        return any(regex.match(tag) for regex in self.ignored_regexes)

    def get_version_tags(
        self, tags: Iterable[GitTag], warn: bool = False
    ) -> list[GitTag]:
        """Filter in version tags and warn on unexpected tags"""
        return [tag for tag in tags if self.is_version_tag(tag, warn)]

    def extract_version(self, tag: GitTag) -> Version:
        """
        Extract a version from the tag as defined in tag formats.

        Raises `InvalidVersion` if the tag does not match any format.
        """
        candidates = (
            m for regex in self.version_regexes if (m := regex.fullmatch(tag.name))
        )
        if not (m := next(candidates, None)):
            raise InvalidVersion(self._version_tag_error(tag.name))
        if "version" in m.groupdict():
            return self.scheme(m.group("version"))

        parts = m.groupdict()
        version = parts["major"]

        if minor := parts.get("minor"):
            version = f"{version}.{minor}"
        if patch := parts.get("patch"):
            version = f"{version}.{patch}"

        if parts.get("prerelease"):
            version = f"{version}-{parts['prerelease']}"
        if parts.get("devrelease"):
            version = f"{version}{parts['devrelease']}"
        return self.scheme(version)

    def include_in_changelog(self, tag: GitTag) -> bool:
        """Check if a tag should be included in the changelog"""
        try:
            version = self.extract_version(tag)
        except InvalidVersion:
            return False
        return not (self.merge_prereleases and version.is_prerelease)

    def search_version(self, text: str, last: bool = False) -> VersionTag | None:
        """
        Search the first or last version tag occurrence in text.

        It searches for complete versions only (aka `major`, `minor` and `patch`)
        """
        candidates = (
            m for regex in self.version_regexes if len(m := list(regex.finditer(text)))
        )
        if not (matches := next(candidates, [])):
            return None

        match = matches[-1 if last else 0]

        if "version" in match.groupdict():
            return VersionTag(match.group("version"), match.group(0))

        parts = match.groupdict()
        try:
            version = f"{parts['major']}.{parts['minor']}.{parts['patch']}"
        except KeyError:
            return None

        if parts.get("prerelease"):
            version = f"{version}-{parts['prerelease']}"
        if parts.get("devrelease"):
            version = f"{version}{parts['devrelease']}"
        return VersionTag(version, match.group(0))

    def normalize_tag(
        self, version: Version | str, tag_format: str | None = None
    ) -> str:
        """
        The tag and the software version might be different.

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
        self, tags: Iterable[GitTag], version: Version | str
    ) -> GitTag | None:
        """Find the first matching tag for a given version."""
        version = self.scheme(version) if isinstance(version, str) else version
        possible_tags = set(self.normalize_tag(version, f) for f in self.tag_formats)
        candidates = [t for t in tags if t.name in possible_tags]
        if len(candidates) > 1:
            warnings.warn(
                UserWarning(
                    f"Multiple tags found for version {version}: {', '.join(t.name for t in candidates)}"
                )
            )
        return next(iter(candidates), None)

    @classmethod
    def from_settings(cls, settings: Settings) -> Self:
        """Extract tag rules from settings"""
        return cls(
            scheme=get_version_scheme(settings),
            tag_format=settings["tag_format"],
            legacy_tag_formats=settings["legacy_tag_formats"],
            ignored_tag_formats=settings["ignored_tag_formats"],
            merge_prereleases=settings["changelog_merge_prerelease"],
        )
