from __future__ import annotations

from pathlib import Path

import tomlkit

from commitizen.providers.base_provider import TomlProvider


class CargoProvider(TomlProvider):
    """
    Cargo version management

    With support for `workspaces`
    """

    filename = "Cargo.toml"
    lock_filename = "Cargo.lock"

    @property
    def lock_file(self) -> Path:
        return Path() / self.lock_filename

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

    def set_version(self, version: str) -> None:
        super().set_version(version)
        if self.lock_file.exists():
            self.set_lock_version(version)

    def set_lock_version(self, version: str) -> None:
        cargo_toml_content = tomlkit.parse(self.file.read_text())
        try:
            package_name = cargo_toml_content["package"]["name"]  # type: ignore
        except tomlkit.exceptions.NonExistentKey:
            package_name = cargo_toml_content["workspace"]["package"]["name"]  # type: ignore

        cargo_lock_content = tomlkit.parse(self.lock_file.read_text())
        packages: tomlkit.items.AoT = cargo_lock_content["package"]  # type: ignore[assignment]
        for i, package in enumerate(packages):
            if package["name"] == package_name:
                cargo_lock_content["package"][i]["version"] = version  # type: ignore[index]
                break
        self.lock_file.write_text(tomlkit.dumps(cargo_lock_content))
