from pathlib import Path

from commitizen import defaults, git

from .base_config import BaseConfig
from .toml_config import TomlConfig


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

        with open(filename, "r") as f:
            data: str = f.read()

        _conf: TomlConfig
        if "toml" in filename.suffix:
            _conf = TomlConfig(data=data, path=filename)

        if _conf.is_empty_config:
            continue
        else:
            conf = _conf
            break

    return conf
