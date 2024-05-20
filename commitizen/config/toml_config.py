from __future__ import annotations

import os
from pathlib import Path

from tomlkit import exceptions, parse, table

from commitizen.exceptions import InvalidConfigurationError

from .base_config import BaseConfig


class TomlConfig(BaseConfig):
    def __init__(self, *, data: bytes | str, path: Path | str):
        super().__init__()
        self.is_empty_config = False
        self.add_path(path)
        self._parse_setting(data)

    def init_empty_config_content(self):
        if os.path.isfile(self.path):
            with open(self.path, "rb") as input_toml_file:
                parser = parse(input_toml_file.read())
        else:
            parser = parse("")

        with open(self.path, "wb") as output_toml_file:
            if parser.get("tool") is None:
                parser["tool"] = table()
            parser["tool"]["commitizen"] = table()
            output_toml_file.write(parser.as_string().encode(self.encoding))

    def set_key(self, key, value):
        """Set or update a key in the conf.

        For now only strings are supported.
        We use to update the version number.
        """
        with open(self.path, "rb") as f:
            parser = parse(f.read())

        parser["tool"]["commitizen"][key] = value
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
            self.settings.update(doc["tool"]["commitizen"])  # type: ignore
        except exceptions.NonExistentKey:
            self.is_empty_config = True
