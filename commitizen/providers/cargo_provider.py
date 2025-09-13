from __future__ import annotations

import fnmatch
import glob
from pathlib import Path

from tomlkit import TOMLDocument, dumps, parse
from tomlkit.exceptions import NonExistentKey
from tomlkit.items import AoT

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

    def get(self, document: TOMLDocument) -> str:
        out = _try_get_workspace(document)["package"]["version"]
        assert isinstance(out, str)
        return out

    def set(self, document: TOMLDocument, version: str) -> None:
        _try_get_workspace(document)["package"]["version"] = version

    def set_version(self, version: str) -> None:
        super().set_version(version)
        if self.lock_file.exists():
            self.set_lock_version(version)

    def set_lock_version(self, version: str) -> None:
        cargo_toml_content = parse(self.file.read_text())
        cargo_lock_content = parse(self.lock_file.read_text())
        packages = cargo_lock_content["package"]

        assert isinstance(packages, AoT)

        try:
            cargo_package_name = cargo_toml_content["package"]["name"]  # type: ignore[index]
            assert isinstance(cargo_package_name, str)
            for i, package in enumerate(packages):
                if package["name"] == cargo_package_name:
                    cargo_lock_content["package"][i]["version"] = version  # type: ignore[index]
                    break
        except NonExistentKey:
            workspace = cargo_toml_content.get("workspace", {})
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
                    package_content = parse(cargo_file.read_text()).get("package", {})
                    assert isinstance(package_content, dict)
                    try:
                        version_workspace = package_content["version"]["workspace"]
                        if version_workspace is True:
                            package_name = package_content["name"]
                            assert isinstance(package_name, str)
                            members_inheriting.append(package_name)
                    except NonExistentKey:
                        pass

            for i, package in enumerate(packages):
                if package["name"] in members_inheriting:
                    cargo_lock_content["package"][i]["version"] = version  # type: ignore[index]

        self.lock_file.write_text(dumps(cargo_lock_content))


def _try_get_workspace(document: TOMLDocument) -> dict:
    try:
        workspace = document["workspace"]
        assert isinstance(workspace, dict)
        return workspace
    except NonExistentKey:
        return document
