from __future__ import annotations

import fnmatch
import glob
from pathlib import Path

import tomlkit

from commitizen.providers.base_provider import TomlProvider


def matches_exclude(path: str, exclude_patterns: list[str]) -> bool:
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False


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
            workspace_members = cargo_toml_content.get("workspace", {}).get(
                "members", []
            )
            excluded_workspace_members = cargo_toml_content.get("workspace", {}).get(
                "exclude", []
            )
            members_inheriting = []

            for member in workspace_members:
                for path in glob.glob(member, recursive=True):
                    if matches_exclude(path, excluded_workspace_members):
                        continue
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
