import warnings
from pathlib import Path
from typing import Optional

from commitizen import defaults, git, out
from commitizen.error_codes import NOT_A_GIT_PROJECT
from .base_config import BaseConfig
from .toml_config import TomlConfig
from .ini_config import IniConfig


def load_global_conf() -> Optional[IniConfig]:
    home = Path.home()
    global_cfg = home / Path(".cz")
    if not global_cfg.exists():
        return None

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

    conf = IniConfig(data)
    return conf


def read_cfg() -> BaseConfig:
    conf = BaseConfig()

    git_project_root = git.find_git_project_root()
    if not git_project_root:
        out.error(
            "fatal: not a git repository (or any of the parent directories): .git"
        )
        raise SystemExit(NOT_A_GIT_PROJECT)

    allowed_cfg_files = defaults.config_files
    cfg_paths = (
        path / Path(filename)
        for path in [Path("."), git_project_root]
        for filename in allowed_cfg_files
    )
    for filename in cfg_paths:
        if not filename.exists():
            continue

        with open(filename, "r") as f:
            data: str = f.read()

        if "toml" in filename.suffix:
            _conf = TomlConfig(data=data, path=filename)
        else:
            warnings.warn(
                ".cz, setup.cfg, and .cz.cfg will be deprecated "
                "in next major version. \n"
                'Please use "pyproject.toml", ".cz.toml" instead'
            )
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
