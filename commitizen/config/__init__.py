from __future__ import annotations

from pathlib import Path

from commitizen import defaults, git
from commitizen.exceptions import ConfigFileNotFound

from .base_config import BaseConfig
from .json_config import JsonConfig
from .toml_config import TomlConfig
from .yaml_config import YAMLConfig


def read_cfg(filepath: str | None = None) -> BaseConfig:
    conf = BaseConfig()

    git_project_root = git.find_git_project_root()

    if filepath is not None:
        given_cfg_path = Path(filepath)

        if not given_cfg_path.exists():
            raise ConfigFileNotFound()

        with open(given_cfg_path, "rb") as f:
            given_cfg_data: bytes = f.read()

        given_cfg: TomlConfig | JsonConfig | YAMLConfig

        if "toml" in given_cfg_path.suffix:
            given_cfg = TomlConfig(data=given_cfg_data, path=given_cfg_path)
        elif "json" in given_cfg_path.suffix:
            given_cfg = JsonConfig(data=given_cfg_data, path=given_cfg_path)
        elif "yaml" in given_cfg_path.suffix:
            given_cfg = YAMLConfig(data=given_cfg_data, path=given_cfg_path)

        return given_cfg

    cfg_search_paths = [Path(".")]
    if git_project_root:
        cfg_search_paths.append(git_project_root)

    cfg_paths = (
        path / Path(filename)
        for path in cfg_search_paths
        for filename in defaults.config_files
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

        if _conf.is_empty_config:
            continue
        else:
            conf = _conf
            break

    return conf
