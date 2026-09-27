from __future__ import annotations

from pathlib import Path

import tomlkit
from packaging.utils import canonicalize_name

from commitizen.providers.pep621_provider import Pep621Provider


class Pep751Provider(Pep621Provider):
    """
    PEP 621 + PEP 751 lockfile awareness

    Updates pyproject.toml (via Pep621Provider) and any pylock*.toml
    lock files that contain a matching local directory package entry.
    """

    lock_patterns: tuple[str, ...] = ("pylock.toml", "pylock.*.toml")

    def set_version(self, version: str) -> None:
        doc = tomlkit.parse(self.file.read_text())
        project_name = canonicalize_name(doc["project"]["name"])  # type: ignore[index,arg-type]

        super().set_version(version)

        for pattern in self.lock_patterns:
            for lock_file in Path().glob(pattern):
                lock_doc = tomlkit.parse(lock_file.read_text())
                updated = False
                for pkg in lock_doc.get("packages", []):
                    if (
                        canonicalize_name(pkg.get("name", "")) == project_name
                        and "directory" in pkg
                    ):
                        pkg["version"] = version
                        updated = True
                if updated:
                    lock_file.write_text(tomlkit.dumps(lock_doc))
