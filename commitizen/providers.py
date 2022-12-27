from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar, cast

import importlib_metadata as metadata
import tomlkit

from commitizen.config.base_config import BaseConfig
from commitizen.exceptions import VersionProviderUnknown

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
        ...

    @abstractmethod
    def set_version(self, version: str):
        """
        Set the new current version
        """
        ...


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
    """

    filename = "Cargo.toml"

    def get(self, document: tomlkit.TOMLDocument) -> str:
        return document["package"]["version"]  # type: ignore

    def set(self, document: tomlkit.TOMLDocument, version: str):
        document["package"]["version"] = version  # type: ignore


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
