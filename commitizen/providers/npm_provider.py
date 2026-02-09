from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from commitizen.providers.base_provider import VersionProvider

if TYPE_CHECKING:
    from collections.abc import Mapping


class NpmProvider(VersionProvider):
    """
    npm package.json and package-lock.json version management
    """

    indent: ClassVar[int] = 2
    package_filename = "package.json"
    lock_filename = "package-lock.json"
    shrinkwrap_filename = "npm-shrinkwrap.json"

    def _get_encoding(self) -> str:
        return self.config.settings["encoding"]

    @property
    def package_file(self) -> Path:
        return Path() / self.package_filename

    @property
    def lock_file(self) -> Path:
        return Path() / self.lock_filename

    @property
    def shrinkwrap_file(self) -> Path:
        return Path() / self.shrinkwrap_filename

    def get_version(self) -> str:
        """
        Get the current version from package.json
        """
        package_document = json.loads(
            self.package_file.read_text(encoding=self._get_encoding())
        )
        return self.get_package_version(package_document)

    def set_version(self, version: str) -> None:
        package_document = self.set_package_version(
            json.loads(
                self.package_file.read_text(encoding=self._get_encoding())
            ),
            version,
        )
        self.package_file.write_text(
            json.dumps(package_document, indent=self.indent, ensure_ascii=False)
            + "\n",
            encoding=self._get_encoding(),
        )
        if self.lock_file.is_file():
            lock_document = self.set_lock_version(
                json.loads(
                    self.lock_file.read_text(encoding=self._get_encoding())
                ),
                version,
            )
            self.lock_file.write_text(
                json.dumps(lock_document, indent=self.indent, ensure_ascii=False)
                + "\n",
                encoding=self._get_encoding(),
            )
        if self.shrinkwrap_file.is_file():
            shrinkwrap_document = self.set_shrinkwrap_version(
                json.loads(
                    self.shrinkwrap_file.read_text(encoding=self._get_encoding())
                ),
                version,
            )
            self.shrinkwrap_file.write_text(
                json.dumps(
                    shrinkwrap_document, indent=self.indent, ensure_ascii=False
                )
                + "\n",
                encoding=self._get_encoding(),
            )

    def get_package_version(self, document: Mapping[str, str]) -> str:
        return document["version"]

    def set_package_version(
        self, document: dict[str, Any], version: str
    ) -> dict[str, Any]:
        document["version"] = version
        return document

    def set_lock_version(
        self, document: dict[str, Any], version: str
    ) -> dict[str, Any]:
        document["version"] = version
        document["packages"][""]["version"] = version
        return document

    def set_shrinkwrap_version(
        self, document: dict[str, Any], version: str
    ) -> dict[str, Any]:
        document["version"] = version
        document["packages"][""]["version"] = version
        return document
