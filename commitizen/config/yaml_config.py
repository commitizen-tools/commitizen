from __future__ import annotations

from pathlib import Path

import yaml

from commitizen.git import smart_open
from commitizen.exceptions import InvalidConfigurationError

from .base_config import BaseConfig


class YAMLConfig(BaseConfig):
    def __init__(self, *, data: bytes | str, path: Path | str):
        super().__init__()
        self.is_empty_config = False
        self.add_path(path)
        self._parse_setting(data)

    def init_empty_config_content(self):
        with smart_open(self.path, "a", encoding=self.encoding) as json_file:
            yaml.dump({"commitizen": {}}, json_file, explicit_start=True)

    def _parse_setting(self, data: bytes | str) -> None:
        """We expect to have a section in cz.yaml looking like

        ```
        commitizen:
          name: cz_conventional_commits
        ```
        """
        import yaml.scanner

        try:
            doc = yaml.safe_load(data)
        except yaml.YAMLError as e:
            raise InvalidConfigurationError(f"Failed to parse {self.path}: {e}")

        try:
            self.settings.update(doc["commitizen"])
        except (KeyError, TypeError):
            self.is_empty_config = True

    def set_key(self, key, value):
        """Set or update a key in the conf.

        For now only strings are supported.
        We use to update the version number.
        """
        with open(self.path, "rb") as yaml_file:
            parser = yaml.load(yaml_file, Loader=yaml.FullLoader)

        parser["commitizen"][key] = value
        with smart_open(self.path, "w", encoding=self.encoding) as yaml_file:
            yaml.dump(parser, yaml_file, explicit_start=True)

        return self
