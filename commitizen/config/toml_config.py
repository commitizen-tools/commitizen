from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from tomlkit import exceptions, parse, table

from commitizen.exceptions import InvalidConfigurationError

from .base_config import BaseConfig

if TYPE_CHECKING:
    import sys

    # Self is Python 3.11+ but backported in typing-extensions
    if sys.version_info < (3, 11):
        from typing_extensions import Self
    else:
        from typing import Self


class TomlConfig(BaseConfig):
    def __init__(self, *, data: bytes | str, path: Path | str) -> None:
        super().__init__()
        self.is_empty_config = False
        self.path = path
        self._parse_setting(data)

    def init_empty_config_content(self) -> None:
        if os.path.isfile(self.path):
            with open(self.path, "rb") as input_toml_file:
                parser = parse(input_toml_file.read())
        else:
            parser = parse("")

        with open(self.path, "wb") as output_toml_file:
            if parser.get("tool") is None:
                parser["tool"] = table()
            parser["tool"]["commitizen"] = table()  # type: ignore[index]
            output_toml_file.write(parser.as_string().encode(self.encoding))

    def set_key(self, key: str, value: Any) -> Self:
        """Set or update a key in the conf.

        For now only strings are supported.
        We use to update the version number.
        """
        with open(self.path, "rb") as f:
            parser = parse(f.read())

        parser["tool"]["commitizen"][key] = value  # type: ignore[index]
        with open(self.path, "wb") as f:
            f.write(parser.as_string().encode(self.encoding))
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
