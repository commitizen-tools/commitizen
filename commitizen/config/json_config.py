import json
from pathlib import Path
from typing import Union

from .base_config import BaseConfig


class JsonConfig(BaseConfig):
    def __init__(self, *, data: Union[bytes, str], path: Union[Path, str]):
        super(JsonConfig, self).__init__()
        self.is_empty_config = False
        self._parse_setting(data)
        self.add_path(path)

    def init_empty_config_content(self):
        with open(self.path, "a") as json_file:
            json.dump({"commitizen": {}}, json_file)

    def set_key(self, key, value):
        """Set or update a key in the conf.

        For now only strings are supported.
        We use to update the version number.
        """
        with open(self.path, "rb") as f:
            parser = json.load(f)

        parser["commitizen"][key] = value
        with open(self.path, "w") as f:
            json.dump(parser, f)
        return self

    def _parse_setting(self, data: Union[bytes, str]):
        """We expect to have a section in .cz.json looking like

        ```
        {
            "commitizen": {
                "name": "cz_conventional_commits"
            }
        }
        ```
        """
        doc = json.loads(data)
        try:
            self.settings.update(doc["commitizen"])
        except KeyError:
            self.is_empty_config = True
