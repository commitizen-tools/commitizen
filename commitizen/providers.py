from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, ClassVar, cast

import importlib_metadata as metadata
import tomlkit

from commitizen.config.base_config import BaseConfig
from commitizen.exceptions import VersionProviderUnknown
from commitizen.git import get_tags
from commitizen.version_schemes import get_version_scheme

PROVIDER_ENTRYPOINT = "commitizen.provider"
DEFAULT_PROVIDER = "commitizen"


class VersionProvider(ABC):
    """
    Abstract base class for version providers.

    Each version provider should inherit and implement this class.
    """

    config: BaseConfig

    def __init__(self, config: BaseConfig):
        self.config = config

    @abstractmethod
    def get_version(self) -> str:
        """
        Get the current version
        """

    @abstractmethod
    def set_version(self, version: str):
        """
        Set the new current version
        """


class CommitizenProvider(VersionProvider):
    """
    Default version provider: Fetch and set version in commitizen config.
    """

    def get_version(self) -> str:
        return self.config.settings["version"]  # type: ignore

    def set_version(self, version: str):
        self.config.set_key("version", version)


class FileProvider(VersionProvider):
    """
    Base class for file-based version providers
    """

    filename: ClassVar[str]

    @property
    def file(self) -> Path:
        return Path() / self.filename


class TomlProvider(FileProvider):
    """
    Base class for TOML-based version providers
    """

    def get_version(self) -> str:
        document = tomlkit.parse(self.file.read_text())
        return self.get(document)

    def set_version(self, version: str):
        document = tomlkit.parse(self.file.read_text())
        self.set(document, version)
        self.file.write_text(tomlkit.dumps(document))

    def get(self, document: tomlkit.TOMLDocument) -> str:
        return document["project"]["version"]  # type: ignore

    def set(self, document: tomlkit.TOMLDocument, version: str):
        document["project"]["version"] = version  # type: ignore


class Pep621Provider(TomlProvider):
    """
    PEP-621 version management
    """

    filename = "pyproject.toml"


class PoetryProvider(TomlProvider):
    """
    Poetry version management
    """

    filename = "pyproject.toml"

    def get(self, pyproject: tomlkit.TOMLDocument) -> str:
        return pyproject["tool"]["poetry"]["version"]  # type: ignore

    def set(self, pyproject: tomlkit.TOMLDocument, version: str):
        pyproject["tool"]["poetry"]["version"] = version  # type: ignore


class CargoProvider(TomlProvider):
    """
    Cargo version management

    With support for `workspaces`
    """

    filename = "Cargo.toml"

    def get(self, document: tomlkit.TOMLDocument) -> str:
        try:
            return document["package"]["version"]  # type: ignore
        except tomlkit.exceptions.NonExistentKey:
            ...
        return document["workspace"]["package"]["version"]  # type: ignore

    def set(self, document: tomlkit.TOMLDocument, version: str):
        try:
            document["workspace"]["package"]["version"] = version  # type: ignore
            return
        except tomlkit.exceptions.NonExistentKey:
            ...
        document["package"]["version"] = version  # type: ignore


class JsonProvider(FileProvider):
    """
    Base class for JSON-based version providers
    """

    indent: ClassVar[int] = 2

    def get_version(self) -> str:
        document = json.loads(self.file.read_text())
        return self.get(document)

    def set_version(self, version: str):
        document = json.loads(self.file.read_text())
        self.set(document, version)
        self.file.write_text(json.dumps(document, indent=self.indent) + "\n")

    def get(self, document: dict[str, Any]) -> str:
        return document["version"]  # type: ignore

    def set(self, document: dict[str, Any], version: str):
        document["version"] = version


class NpmProvider(JsonProvider):
    """
    npm package.json version management
    """

    filename = "package.json"


class ComposerProvider(JsonProvider):
    """
    Composer version management
    """

    filename = "composer.json"
    indent = 4


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

    def _tag_format_matcher(self) -> Callable[[str], str | None]:
        version_scheme = get_version_scheme(self.config)
        pattern = (
            self.config.settings.get("tag_format") or version_scheme.parser.pattern
        )
        for var, tag_pattern in self.TAG_FORMAT_REGEXS.items():
            pattern = pattern.replace(var, tag_pattern)

        regex = re.compile(f"^{pattern}$", re.VERBOSE)

        def matcher(tag: str) -> str | None:
            match = regex.match(tag)
            if not match:
                return None
            groups = match.groupdict()
            if "version" in groups:
                return groups["version"]
            elif "major" in groups:
                return "".join(
                    (
                        groups["major"],
                        f".{groups['minor']}" if groups.get("minor") else "",
                        f".{groups['patch']}" if groups.get("patch") else "",
                        groups["prerelease"] if groups.get("prerelease") else "",
                        groups["devrelease"] if groups.get("devrelease") else "",
                    )
                )
            elif pattern == version_scheme.parser.pattern:
                return str(version_scheme(tag))
            return None

        return matcher

    def get_version(self) -> str:
        matcher = self._tag_format_matcher()
        return next(
            (cast(str, matcher(t.name)) for t in get_tags() if matcher(t.name)), "0.0.0"
        )

    def set_version(self, version: str):
        # Not necessary
        pass


def get_provider(config: BaseConfig) -> VersionProvider:
    """
    Get the version provider as defined in the configuration

    :raises VersionProviderUnknown: if the provider named by `version_provider` is not found.
    """
    provider_name = config.settings["version_provider"] or DEFAULT_PROVIDER
    try:
        (ep,) = metadata.entry_points(name=provider_name, group=PROVIDER_ENTRYPOINT)
    except ValueError:
        raise VersionProviderUnknown(f'Version Provider "{provider_name}" unknown.')
    provider_cls = ep.load()
    return cast(VersionProvider, provider_cls(config))
