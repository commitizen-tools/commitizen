from __future__ import annotations

import json
from typing import TYPE_CHECKING

from commitizen.exceptions import InvalidConfigurationError
from commitizen.git import smart_open

from .base_config import BaseConfig

if TYPE_CHECKING:
    import sys
    from pathlib import Path

    # Self is Python 3.11+ but backported in typing-extensions
    if sys.version_info < (3, 11):
        from typing_extensions import Self
    else:
        from typing import Self


class JsonConfig(BaseConfig):
    def __init__(self, *, data: bytes | str, path: Path) -> None:
        super().__init__()
        self.path = path
        self._parse_setting(data)

    def init_empty_config_content(self) -> None:
        with smart_open(
            self.path, "a", encoding=self._settings["encoding"]
        ) as json_file:
            json.dump({"commitizen": {}}, json_file)

    def set_key(self, key: str, value: object) -> Self:
        with open(self.path, "rb") as f:
            config_doc = json.load(f)

        config_doc["commitizen"][key] = value
        with smart_open(self.path, "w", encoding=self._settings["encoding"]) as f:
            json.dump(config_doc, f, indent=2)
        return self

    def _parse_setting(self, data: bytes | str) -> None:
        """We expect to have a section in .cz.json looking like

        ```
        {
            "commitizen": {
                "name": "cz_conventional_commits"
            }
        }
        ```
        """
        try:
            doc = json.loads(data)
        except json.JSONDecodeError as e:
            raise InvalidConfigurationError(f"Failed to parse {self.path}: {e}")

        try:
            self.settings.update(doc["commitizen"])
        except KeyError:
            self.is_empty_config = True
