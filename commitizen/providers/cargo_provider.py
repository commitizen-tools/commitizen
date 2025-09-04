from __future__ import annotations

import glob
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
        # If there is a root package, change its version (but not the workspace version)
        try:
            return document["package"]["version"]  # type: ignore[index,return-value]
        # Else, bump the workspace version
        except tomlkit.exceptions.NonExistentKey:
            ...
        return document["workspace"]["package"]["version"]  # type: ignore[index,return-value]

    def set(self, document: tomlkit.TOMLDocument, version: str) -> None:
        try:
            document["workspace"]["package"]["version"] = version  # type: ignore[index]
            return
        except tomlkit.exceptions.NonExistentKey:
            ...
        document["package"]["version"] = version  # type: ignore[index]

    def set_version(self, version: str) -> None:
        super().set_version(version)
        if self.lock_file.exists():
            self.set_lock_version(version)

    def set_lock_version(self, version: str) -> None:
        cargo_toml_content = tomlkit.parse(self.file.read_text())
        cargo_lock_content = tomlkit.parse(self.lock_file.read_text())
        packages: tomlkit.items.AoT = cargo_lock_content["package"]  # type: ignore[assignment]
        try:
            package_name = cargo_toml_content["package"]["name"]  # type: ignore[index]
            for i, package in enumerate(packages):
                if package["name"] == package_name:
                    cargo_lock_content["package"][i]["version"] = version  # type: ignore[index]
                    break
        except tomlkit.exceptions.NonExistentKey:
            workspace_members = (
                cargo_toml_content.get("workspace", {})
                .get("package", {})
                .get("members", [])
            )
            members_inheriting = []

            for member in workspace_members:
                matched_paths = glob.glob(member, recursive=True)
                for path in matched_paths:
                    cargo_file = Path(path) / "Cargo.toml"
                    cargo_toml_content = tomlkit.parse(cargo_file.read_text())
                    try:
                        version_workspace = cargo_toml_content["package"]["version"][  # type: ignore[index]
                            "workspace"
                        ]
                        if version_workspace is True:
                            package_name = cargo_toml_content["package"]["name"]  # type: ignore[index]
                            members_inheriting.append(package_name)
                    except tomlkit.exceptions.NonExistentKey:
                        continue

            for i, package in enumerate(packages):
                if package["name"] in members_inheriting:
                    cargo_lock_content["package"][i]["version"] = version  # type: ignore[index]

        self.lock_file.write_text(tomlkit.dumps(cargo_lock_content))
