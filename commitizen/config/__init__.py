from pathlib import Path
from typing import Union

from commitizen import defaults, git

from .base_config import BaseConfig
from .json_config import JsonConfig
from .toml_config import TomlConfig
from .yaml_config import YAMLConfig


def read_cfg() -> BaseConfig:
    conf = BaseConfig()

    git_project_root = git.find_git_project_root()
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

        _conf: Union[TomlConfig, JsonConfig, YAMLConfig]

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
