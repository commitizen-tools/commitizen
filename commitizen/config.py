import configparser
import json
import os
import warnings
from typing import Optional
from pathlib import Path
from tomlkit import parse, exceptions

from commitizen import defaults


class Config:
    def __init__(self):
        self._config = defaults.settings.copy()
        self._path: Optional[str] = None

    @property
    def config(self):
        return self._config

    @property
    def path(self):
        return self._path

    def update(self, data: dict):
        self._config.update(data)

    def add_path(self, path: str):
        self._path = path


_conf = Config()


def has_pyproject() -> bool:
    return os.path.isfile("pyproject.toml")


def read_pyproject_conf(data: str) -> dict:
    """We expect to have a section in pyproject looking like

    ```
    [tool.commitizen]
    name = "cz_conventional_commits"
    ```
    """
    doc = parse(data)
    try:
        return doc["tool"]["commitizen"]
    except exceptions.NonExistentKey:
        return {}


def read_raw_parser_conf(data: str) -> dict:
    """We expect to have a section like this

    ```
    [commitizen]
    name = cz_jira
    files = [
        "commitizen/__version__.py",
        "pyproject.toml"
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

        return _data

    except KeyError:
        return {}


def load_global_conf() -> dict:
    home = str(Path.home())
    global_cfg = os.path.join(home, ".cz")
    if not os.path.exists(global_cfg):
        return {}

    # global conf doesnt make sense with commitizen bump
    # so I'm deprecating it and won't test it
    message = (
        "Global conf will be deprecated in next major version. "
        "Use per project configuration. "
        "Remove '~/.cz' file from your conf folder."
    )
    warnings.simplefilter("always", DeprecationWarning)
    warnings.warn(message, category=DeprecationWarning)

    with open(global_cfg, "r") as f:
        data = f.read()
    conf = read_raw_parser_conf(data)
    return conf


def read_cfg() -> dict:
    allowed_cfg_files = defaults.config_files

    for filename in allowed_cfg_files:
        config_file_exists = os.path.exists(filename)
        if not config_file_exists:
            continue
        with open(filename, "r") as f:
            data: str = f.read()
        if "toml" in filename:
            conf = read_pyproject_conf(data)
        else:
            conf = read_raw_parser_conf(data)
        if not conf:
            continue

        _conf.update(conf)
        _conf.add_path(filename)
        return _conf.config

    if not _conf.path:
        conf = load_global_conf()
        if conf:
            _conf.update(conf)
    return _conf.config


def set_key(key: str, value: str) -> dict:
    """Set or update a key in the conf.

    For now only strings are supported.
    We use to update the version number.
    """
    if not _conf.path:
        return {}

    if "toml" in _conf.path:
        with open(_conf.path, "r") as f:
            parser = parse(f.read())
        parser["tool"]["commitizen"][key] = value
        with open(_conf.path, "w") as f:
            f.write(parser.as_string())
    else:
        parser = configparser.ConfigParser()
        parser.read(_conf.path)
        parser["commitizen"][key] = value
        with open(_conf.path, "w") as f:
            parser.write(f)

    return _conf.config
