from __future__ import annotations

from pathlib import Path

from commitizen import defaults, git
from commitizen.config.factory import create_config
from commitizen.exceptions import ConfigFileIsEmpty, ConfigFileNotFound

from .base_config import BaseConfig


def _try_read_config_file(filename: Path) -> BaseConfig | None:
    with open(filename, "rb") as f:
        data: bytes = f.read()

    conf = create_config(data=data, path=filename)
    if not conf.is_empty_config:
        return conf

    return None


def search_and_read_config_file(specified_config_path: str | None = None) -> BaseConfig:
    """Search and read config file from specified path, current directory, or git project root. If not found, return empty config object.

    Args:
        specified_config_path (str | None, optional): from --config command line argument. Defaults to None.

    Raises:
        ConfigFileNotFound: specified config file not found
        ConfigFileIsEmpty: specified config file is empty

    Returns:
        BaseConfig: config object
    """
    if specified_config_path is not None:
        out_path = Path(specified_config_path)
        if not out_path.exists():
            raise ConfigFileNotFound()

        if (ret := _try_read_config_file(out_path)) is not None:
            return ret
        raise ConfigFileIsEmpty()

    cfg_search_paths = [Path(".")]
    if git_project_root := git.find_git_project_root():
        cfg_search_paths.append(git_project_root)

    for path in cfg_search_paths:
        for filename in defaults.CONFIG_FILES:
            out_path = path / Path(filename)
            if (
                out_path.exists()
                and (ret := _try_read_config_file(out_path)) is not None
            ):
                return ret

    # TODO: add comment about why we return empty config object
    return BaseConfig()
