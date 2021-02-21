from pathlib import Path
from typing import Union

import yaml

from .base_config import BaseConfig


class YAMLConfig(BaseConfig):
    def __init__(self, *, data: Union[bytes, str], path: Union[Path, str]):
        super(YAMLConfig, self).__init__()
        self.is_empty_config = False
        self._parse_setting(data)
        self.add_path(path)

    def init_empty_config_content(self):
        with open(self.path, "a") as json_file:
            yaml.dump({"commitizen": {}}, json_file)

    def _parse_setting(self, data: Union[bytes, str]):
        """We expect to have a section in cz.yaml looking like

        ```
        commitizen:
          name: cz_conventional_commits
        ```
        """
        doc = yaml.safe_load(data)
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
        with open(self.path, "w") as yaml_file:
            yaml.dump(parser, yaml_file)

        return self
