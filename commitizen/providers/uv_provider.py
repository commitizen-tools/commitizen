from __future__ import annotations

from pathlib import Path

import tomlkit
import tomlkit.items
from packaging.utils import canonicalize_name

from commitizen.providers.base_provider import TomlProvider


class UvProvider(TomlProvider):
    """
    uv.lock and pyproject.toml version management
    """

    filename = "pyproject.toml"
    lock_filename = "uv.lock"

    @property
    def lock_file(self) -> Path:
        return Path() / self.lock_filename

    def set_version(self, version: str) -> None:
        super().set_version(version)
        self.set_lock_version(version)

    def set_lock_version(self, version: str) -> None:
        pyproject_toml_content = tomlkit.parse(self.file.read_text())
        project_name = pyproject_toml_content["project"]["name"]  # type: ignore[index]
        normalized_project_name = canonicalize_name(str(project_name))

        document = tomlkit.parse(self.lock_file.read_text())

        packages: tomlkit.items.AoT = document["package"]  # type: ignore[assignment]
        for i, package in enumerate(packages):
            if package["name"] == normalized_project_name:
                document["package"][i]["version"] = version  # type: ignore[index]
                break
        self.lock_file.write_text(tomlkit.dumps(document))
