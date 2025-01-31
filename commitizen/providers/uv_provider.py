from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import tomlkit

from commitizen.providers.base_provider import TomlProvider

if TYPE_CHECKING:
    import tomlkit.items


class UvProvider(TomlProvider):
    """
    uv.lock and pyproject.tom version management
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

        document = tomlkit.parse(self.lock_file.read_text())

        packages: tomlkit.items.AoT = document["package"]  # type: ignore[assignment]
        for i, package in enumerate(packages):
            if package["name"] == project_name:
                document["package"][i]["version"] = version  # type: ignore[index]
                break
        self.lock_file.write_text(tomlkit.dumps(document))
