from __future__ import annotations

from typing import TYPE_CHECKING

from commitizen.providers.base_provider import TomlProvider

if TYPE_CHECKING:
    import tomlkit


class PoetryProvider(TomlProvider):
    """
    Poetry version management
    """

    filename = "pyproject.toml"

    def get(self, document: tomlkit.TOMLDocument) -> str:
        return document["tool"]["poetry"]["version"]  # type: ignore  # noqa: PGH003

    def set(self, document: tomlkit.TOMLDocument, version: str) -> None:
        document["tool"]["poetry"]["version"] = version  # type: ignore  # noqa: PGH003
