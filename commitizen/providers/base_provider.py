from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

import tomlkit

from commitizen.git import smart_open

if TYPE_CHECKING:
    from collections.abc import Mapping

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

    def _get_encoding(self) -> str:
        return self.config.settings["encoding"]

    def _write_text(self, path: Path, content: str) -> None:
        """Write `content` to `path` with the configured encoding.

        The file is opened with `smart_open`, so the line ending follows
        `git config core.eol`, as it does for `version_files` and the changelog.
        """
        with smart_open(path, "w", encoding=self._get_encoding()) as file:
            file.write(content)


class JsonProvider(FileProvider):
    """
    Base class for JSON-based version providers
    """

    indent: ClassVar[int] = 2

    def get_version(self) -> str:
        document = json.loads(self.file.read_text(encoding=self._get_encoding()))
        return self.get(document)

    def set_version(self, version: str) -> None:
        document = json.loads(self.file.read_text(encoding=self._get_encoding()))
        self.set(document, version)
        self._write_text(self.file, json.dumps(document, indent=self.indent) + "\n")

    def get(self, document: Mapping[str, str]) -> str:
        return document["version"]

    def set(self, document: dict[str, Any], version: str) -> None:
        document["version"] = version


class TomlProvider(FileProvider):
    """
    Base class for TOML-based version providers
    """

    def get_version(self) -> str:
        document = tomlkit.parse(self.file.read_text(encoding=self._get_encoding()))
        return self.get(document)

    def set_version(self, version: str) -> None:
        document = tomlkit.parse(self.file.read_text(encoding=self._get_encoding()))
        self.set(document, version)
        self._write_text(self.file, tomlkit.dumps(document))

    def get(self, document: tomlkit.TOMLDocument) -> str:
        return document["project"]["version"]  # type: ignore[index,return-value]

    def set(self, document: tomlkit.TOMLDocument, version: str) -> None:
        document["project"]["version"] = version  # type: ignore[index]
