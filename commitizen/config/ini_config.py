import configparser
import json
import warnings

from .base_config import BaseConfig


class IniConfig(BaseConfig):
    def __init__(self, *, data: str, path: str):
        warnings.simplefilter("always", DeprecationWarning)
        warnings.warn(
            (
                ".cz, setup.cfg, and .cz.cfg will be deprecated "
                "in next major version. \n"
                'Please use "pyproject.toml", ".cz.toml" instead'
            ),
            category=DeprecationWarning,
        )

        super(IniConfig, self).__init__()
        self.is_empty_config = False
        self._parse_setting(data)
        self.add_path(path)

    def set_key(self, key, value):
        """Set or update a key in the conf.

        For now only strings are supported.
        We use to update the version number.
        """
        parser = configparser.ConfigParser()
        parser.read(self.path)
        parser["commitizen"][key] = value
        with open(self.path, "w") as f:
            parser.write(f)
        return self

    def _parse_setting(self, data: str):
        """We expect to have a section like this

        ```
        [commitizen]
        name = cz_jira
        files = [
            "commitizen/__version__.py",
            "pyproject.toml"
            ]  # this tab at the end is important
        style = [
            ["pointer", "reverse"],
            ["question", "underline"]
            ]  # this tab at the end is important
        ```
        """
        config = configparser.ConfigParser(allow_no_value=True)
        config.read_string(data)
        try:
            _data: dict = dict(config["commitizen"])
            if "files" in _data:
                files = _data["files"]
                _f = json.loads(files)
                _data.update({"files": _f})
            if "style" in _data:
                style = _data["style"]
                _s = json.loads(style)
                _data.update({"style": _s})

            self._settings.update(_data)
        except KeyError:
            self.is_empty_config = True
