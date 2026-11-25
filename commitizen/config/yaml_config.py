from __future__ import annotations

from typing import TYPE_CHECKING, Any

import yaml

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


class YAMLConfig(BaseConfig):
    _parse_errors = (yaml.YAMLError,)
    _missing_section_errors = (KeyError, TypeError)

    def __init__(self, *, data: bytes | str, path: Path) -> None:
        super().__init__()
        self.path = path
        self._parse_setting(data)

    def init_empty_config_content(self) -> None:
        with smart_open(
            self.path, "a", encoding=self._settings["encoding"]
        ) as json_file:
            yaml.dump({"commitizen": {}}, json_file, explicit_start=True)

    def contains_commitizen_section(self) -> bool:
        with self.path.open("rb") as yaml_file:
            config_doc = yaml.load(yaml_file, Loader=yaml.FullLoader)
        return config_doc is not None and config_doc.get("commitizen") is not None

    def _load_document(self, data: bytes | str) -> Any:
        """We expect to have a section in cz.yaml looking like

        ```
        commitizen:
          name: cz_conventional_commits
        ```
        """
        return yaml.safe_load(data)

    def _get_commitizen_section(self, doc: Any) -> Any:
        return doc["commitizen"]

    def set_key(self, key: str, value: object) -> Self:
        with self.path.open("rb") as yaml_file:
            config_doc = yaml.load(yaml_file, Loader=yaml.FullLoader)

        config_doc["commitizen"][key] = value
        with smart_open(
            self.path, "w", encoding=self._settings["encoding"]
        ) as yaml_file:
            yaml.dump(config_doc, yaml_file, explicit_start=True)

        return self
