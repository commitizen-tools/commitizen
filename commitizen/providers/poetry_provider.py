from __future__ import annotations

import tomlkit

from commitizen.providers.base_provider import TomlProvider


class PoetryProvider(TomlProvider):
    """
    Poetry version management
    """

    filename = "pyproject.toml"

    def get(self, pyproject: tomlkit.TOMLDocument) -> str:
        return pyproject["tool"]["poetry"]["version"]  # type: ignore[index,return-value]

    def set(self, pyproject: tomlkit.TOMLDocument, version: str) -> None:
        pyproject["tool"]["poetry"]["version"] = version  # type: ignore[index]
