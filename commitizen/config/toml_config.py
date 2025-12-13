from __future__ import annotations

import os
from typing import TYPE_CHECKING

from tomlkit import TOMLDocument, exceptions, parse, table

from commitizen.exceptions import InvalidConfigurationError

from .base_config import BaseConfig

if TYPE_CHECKING:
    import sys
    from pathlib import Path

    # Self is Python 3.11+ but backported in typing-extensions
    if sys.version_info < (3, 11):
        from typing_extensions import Self
    else:
        from typing import Self


class TomlConfig(BaseConfig):
    def __init__(self, *, data: bytes | str, path: Path) -> None:
        super().__init__()
        self.path = path
        self._parse_setting(data)

    def init_empty_config_content(self) -> None:
        config_doc = TOMLDocument()
        if os.path.isfile(self.path):
            with open(self.path, "rb") as input_toml_file:
                config_doc = parse(input_toml_file.read())

        if config_doc.get("tool") is None:
            config_doc["tool"] = table()
        config_doc["tool"]["commitizen"] = table()  # type: ignore[index]

        with open(self.path, "wb") as output_toml_file:
            output_toml_file.write(
                config_doc.as_string().encode(self._settings["encoding"])
            )

    def set_key(self, key: str, value: object) -> Self:
        with open(self.path, "rb") as f:
            config_doc = parse(f.read())

        config_doc["tool"]["commitizen"][key] = value  # type: ignore[index]
        with open(self.path, "wb") as f:
            f.write(config_doc.as_string().encode(self._settings["encoding"]))

        return self

    def _parse_setting(self, data: bytes | str) -> None:
        """We expect to have a section in pyproject looking like

        ```
        [tool.commitizen]
        name = "cz_conventional_commits"
        ```
        """
        try:
            doc = parse(data)
        except exceptions.ParseError as e:
            raise InvalidConfigurationError(f"Failed to parse {self.path}: {e}")

        try:
            self.settings.update(doc["tool"]["commitizen"])  # type: ignore[index,typeddict-item] # TODO: fix this
        except exceptions.NonExistentKey:
            self.is_empty_config = True
