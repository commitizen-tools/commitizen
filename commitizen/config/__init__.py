import warnings
from pathlib import Path
from typing import Optional, Union

from commitizen import defaults, git
from commitizen.exceptions import NotAGitProjectError

from .base_config import BaseConfig
from .ini_config import IniConfig
from .toml_config import TomlConfig


def load_global_conf() -> Optional[IniConfig]:
    home = Path.home()
    global_cfg = home / Path(".cz")
    if not global_cfg.exists():
        return None

    # global conf doesn't make sense with commitizen bump
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

    conf = IniConfig(data=data, path=global_cfg)
    return conf


def read_cfg() -> BaseConfig:
    conf = BaseConfig()

    git_project_root = git.find_git_project_root()
    if not git_project_root:
        raise NotAGitProjectError()

    cfg_paths = (
        path / Path(filename)
        for path in [Path("."), git_project_root]
        for filename in defaults.config_files
    )
    for filename in cfg_paths:
        if not filename.exists():
            continue

        with open(filename, "r") as f:
            data: str = f.read()

        _conf: Union[TomlConfig, IniConfig]
        if "toml" in filename.suffix:
            _conf = TomlConfig(data=data, path=filename)
        else:
            _conf = IniConfig(data=data, path=filename)

        if _conf.is_empty_config:
            continue
        else:
            conf = _conf
            break

    if not conf.path:
        global_conf = load_global_conf()
        if global_conf:
            conf = global_conf

    return conf
