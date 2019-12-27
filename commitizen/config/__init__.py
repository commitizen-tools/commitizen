import os
import warnings
from pathlib import Path
from typing import Optional

from commitizen import defaults
from .base_config import BaseConfig
from .toml_config import TomlConfig
from .ini_config import IniConfig


def load_global_conf() -> Optional[IniConfig]:
    home = str(Path.home())
    global_cfg = os.path.join(home, ".cz")
    if not os.path.exists(global_cfg):
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

    allowed_cfg_files = defaults.config_files
    for filename in allowed_cfg_files:
        config_file_exists = os.path.exists(filename)
        if not config_file_exists:
            continue

        with open(filename, "r") as f:
            data: str = f.read()

        if "toml" in filename:
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
