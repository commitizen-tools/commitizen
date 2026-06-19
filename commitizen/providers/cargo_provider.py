from __future__ import annotations

import fnmatch
import glob
from pathlib import Path
from typing import TYPE_CHECKING

from tomlkit import TOMLDocument, dumps, parse
from tomlkit.exceptions import NonExistentKey

from commitizen.providers.base_provider import TomlProvider

if TYPE_CHECKING:
    from tomlkit.items import AoT


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

    def get(self, document: TOMLDocument) -> str:
        out = _try_get_workspace(document)["package"]["version"]
        if TYPE_CHECKING:
            assert isinstance(out, str)
        return out

    def set(self, document: TOMLDocument, version: str) -> None:
        _try_get_workspace(document)["package"]["version"] = version

        if document.get("workspace"):
            # get all workspace members that have a version.workspace = true
            members_inheriting = _get_workspace_members(document, self._get_encoding())

            # get all workspace dependencies that have a version specified and match a member inheriting
            workspace_deps = document["workspace"].get("dependencies", {})
            for dep_name, dep_value in workspace_deps.items():
                if isinstance(dep_value, str) and (dep_name in members_inheriting):                    
                    workspace_deps[dep_name] = version
                elif (isinstance(dep_value, dict) and dep_value.get("version", [])):
                    if dep_value.get("path", "") and dep_value.get("package", ""):
                        crate_name = dep_value["package"]
                    else:
                        crate_name = dep_name

                    if crate_name in members_inheriting:
                        dep_value["version"] = version

    def set_version(self, version: str) -> None:
        super().set_version(version)
        if self.lock_file.is_file():
            self.set_lock_version(version)

    def set_lock_version(self, version: str) -> None:
        cargo_toml_content = parse(self.file.read_text(encoding=self._get_encoding()))
        cargo_lock_content = parse(
            self.lock_file.read_text(encoding=self._get_encoding())
        )
        packages = cargo_lock_content["package"]

        if TYPE_CHECKING:
            assert isinstance(packages, AoT)

        try:
            cargo_package_name = cargo_toml_content["package"]["name"]  # type: ignore[index]
            if TYPE_CHECKING:
                assert isinstance(cargo_package_name, str)
            for i, package in enumerate(packages):
                if package["name"] == cargo_package_name:
                    cargo_lock_content["package"][i]["version"] = version  # type: ignore[index]
                    break
        except NonExistentKey:
            members_inheriting = _get_workspace_members(cargo_toml_content, self._get_encoding())

            for i, package in enumerate(packages):
                if package["name"] in members_inheriting:
                    cargo_lock_content["package"][i]["version"] = version  # type: ignore[index]

        self.lock_file.write_text(
            dumps(cargo_lock_content), encoding=self._get_encoding()
        )


def _try_get_workspace(document: TOMLDocument) -> dict:
    try:
        workspace = document["workspace"]
        if TYPE_CHECKING:
            assert isinstance(workspace, dict)
        return workspace
    except NonExistentKey:
        return document

def _get_workspace_members(cargo_toml_content: TOMLDocument, encoding: str | None) -> list[str]:
    workspace = cargo_toml_content.get("workspace", {})
    if TYPE_CHECKING:
        assert isinstance(workspace, dict)
    workspace_members = workspace.get("members", [])
    excluded_workspace_members = workspace.get("exclude", [])
    members_inheriting: list[str] = []

    for member in workspace_members:
        for path in glob.glob(member, recursive=True):
            if any(
                fnmatch.fnmatch(path, pattern)
                for pattern in excluded_workspace_members
            ):
                continue

            cargo_file = Path(path) / "Cargo.toml"
            package_content = parse(
                cargo_file.read_text(encoding=encoding)
            ).get("package", {})
            if TYPE_CHECKING:
                assert isinstance(package_content, dict)
            try:
                if not isinstance(package_content["version"], str):
                    version_workspace = package_content["version"]["workspace"]
                    if version_workspace is True:
                        package_name = package_content["name"]
                        if TYPE_CHECKING:
                            assert isinstance(package_name, str)
                        members_inheriting.append(package_name)
            except NonExistentKey:
                pass
    
    return members_inheriting