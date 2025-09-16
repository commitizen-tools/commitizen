from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

import tomlkit

from commitizen.config.base_config import BaseConfig


class VersionProvider(ABC):
    """
    Abstract base class for version providers.

    Each version provider should inherit and implement this class.
    """

    config: BaseConfig

    def __init__(self, config: BaseConfig) -> None:
        self.config = config

    @abstractmethod
    def get_version(self) -> str:
        """
        Get the current version
        """

    @abstractmethod
    def set_version(self, version: str) -> None:
        """
        Set the new current version
        """


class FileProvider(VersionProvider):
    """
    Base class for file-based version providers
    """

    filename: ClassVar[str]

    @property
    def file(self) -> Path:
        return Path() / self.filename


class JsonProvider(FileProvider):
    """
    Base class for JSON-based version providers
    """

    indent: ClassVar[int] = 2

    def get_version(self) -> str:
        version = json.loads(self.file.read_text())["version"]
        assert isinstance(version, str)
        return version

    def set_version(self, version: str) -> None:
        document = json.loads(self.file.read_text())
        document["version"] = version
        self.file.write_text(json.dumps(document, indent=self.indent) + "\n")


class TomlProvider(FileProvider):
    """
    Base class for TOML-based version providers
    """

    def get_version(self) -> str:
        version = tomlkit.parse(self.file.read_text())["project"]["version"]  # type: ignore[index]
        assert isinstance(version, str)
        return version

    def set_version(self, version: str) -> None:
        document = tomlkit.parse(self.file.read_text())
        document["project"]["version"] = version  # type: ignore[index]
        self.file.write_text(tomlkit.dumps(document))
