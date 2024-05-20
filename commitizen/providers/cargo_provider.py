from __future__ import annotations

import tomlkit

from commitizen.providers.base_provider import TomlProvider


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
