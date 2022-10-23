import json
from pathlib import Path
from typing import Union

from commitizen.git import smart_open

from .base_config import BaseConfig


class JsonConfig(BaseConfig):
    def __init__(self, *, data: Union[bytes, str], path: Union[Path, str]):
        super(JsonConfig, self).__init__()
        self.encoding = self.settings["encoding"]
        self.is_empty_config = False
        self._parse_setting(data)
        self.add_path(path)

    def init_empty_config_content(self):
        with smart_open(self.path, "a", encoding=self.encoding) as json_file:
            json.dump({"commitizen": {}}, json_file)

    def set_key(self, key, value):
        """Set or update a key in the conf.

        For now only strings are supported.
        We use to update the version number.
        """
        with open(self.path, "rb") as f:
            parser = json.load(f)

        parser["commitizen"][key] = value
        with smart_open(self.path, "w", encoding=self.encoding) as f:
            json.dump(parser, f, indent=2)
        return self

    def _parse_setting(self, data: Union[bytes, str]) -> None:
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
