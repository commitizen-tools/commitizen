from __future__ import annotations

from pathlib import Path

from commitizen import defaults, git
from commitizen.exceptions import ConfigFileIsEmpty, ConfigFileNotFound

from .base_config import BaseConfig
from .json_config import JsonConfig
from .toml_config import TomlConfig
from .yaml_config import YAMLConfig


def read_cfg(filepath: str | None = None) -> BaseConfig:
    conf = BaseConfig()

    if filepath is not None:
        if not Path(filepath).exists():
            raise ConfigFileNotFound()

        cfg_paths = (path for path in (Path(filepath),))
    else:
        git_project_root = git.find_git_project_root()
        cfg_search_paths = [Path(".")]
        if git_project_root:
            cfg_search_paths.append(git_project_root)

        cfg_paths = (
            path / Path(filename)
            for path in cfg_search_paths
            for filename in defaults.CONFIG_FILES
        )

    for filename in cfg_paths:
        if not filename.exists():
            continue

        _conf: TomlConfig | JsonConfig | YAMLConfig

        with open(filename, "rb") as f:
            data: bytes = f.read()

        if "toml" in filename.suffix:
            _conf = TomlConfig(data=data, path=filename)
        elif "json" in filename.suffix:
            _conf = JsonConfig(data=data, path=filename)
        elif "yaml" in filename.suffix:
            _conf = YAMLConfig(data=data, path=filename)

        if filepath is not None and _conf.is_empty_config:
            raise ConfigFileIsEmpty()
        elif _conf.is_empty_config:
            continue
        else:
            conf = _conf
            break

    return conf
