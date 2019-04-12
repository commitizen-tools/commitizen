import configparser
import os
import warnings
from pathlib import Path
from tomlkit import parse, exceptions

from commitizen import defaults


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
    ```
    """
    config = configparser.ConfigParser(allow_no_value=True)
    config.read_string(data)
    try:
        return dict(config["commitizen"])
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
    warnings.simplefilter('always', DeprecationWarning)
    warnings.warn(message, category=DeprecationWarning)

    with open(global_cfg, "r") as f:
        data = f.read()
    conf = read_raw_parser_conf(data)
    return conf


def read_cfg() -> dict:
    settings = defaults.settings.copy()
    allowed_cfg_files = defaults.config_files
    found_conf = False
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
        found_conf = True
        settings.update(conf)
        return settings

    if not found_conf:
        conf = load_global_conf()
        if conf:
            settings.update(conf)
    return settings
