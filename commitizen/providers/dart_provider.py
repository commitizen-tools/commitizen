from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from commitizen.providers.base_provider import VersionProvider


class DartProvider(VersionProvider):
    """
    dart pubspec.yaml version management
    """

    package_filename = "pubspec.yaml"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._yaml = YAML()
        self._yaml.preserve_quotes = True
        self._yaml.indent(mapping=2, sequence=4, offset=2)

    @property
    def package_file(self) -> Path:
        return Path() / self.package_filename

    def get_version(self) -> str:
        print(self.package_file.read_text())
        document = self._yaml.load(self.package_file.read_text())
        return self.get(document)

    def set_version(self, version: str) -> None:
        document = self._yaml.load(self.package_file.read_text())
        self.set(document, version)
        self._yaml.dump(document, self.package_file)

    def get(self, document: Mapping[str, str]) -> str:
        # Extract the version without the build number
        version = document["version"]
        return version.split("+")[0] if "+" in version else version

    def set(self, document: dict[str, Any], version: str) -> None:
        # To enforce to save the version in pubspec without quotes
        # even if the version could be interpreted as float by yaml
        # dump
        version_value: Any
        try:
            version_value = float(version)
        except ValueError:
            version_value = version
        document["version"] = version_value
