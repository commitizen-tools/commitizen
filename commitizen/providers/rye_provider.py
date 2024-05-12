from __future__ import annotations

import tomlkit


from commitizen.providers.base_provider import TomlProvider


class RyeProvider(TomlProvider):
    """
    Rye version management
    """

    filename = "pyproject.toml"

    def get(self, pyproject: tomlkit.TOMLDocument) -> str:
        return pyproject["tool"]["rye"]["version"]  # type: ignore

    def set(self, pyproject: tomlkit.TOMLDocument, version: str):
        pyproject["tool"]["rye"]["version"] = version  # type: ignore
