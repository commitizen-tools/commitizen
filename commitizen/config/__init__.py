from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from commitizen import defaults, git
from commitizen.config.factory import create_config
from commitizen.exceptions import ConfigFileIsEmpty, ConfigFileNotFound

from .base_config import BaseConfig

if TYPE_CHECKING:
    from collections.abc import Generator


def _resolve_config_paths(filepath: str | None = None) -> Generator[Path, None, None]:
    if filepath is not None:
        out_path = Path(filepath)
        if not out_path.exists():
            raise ConfigFileNotFound()

        yield out_path
        return

    git_project_root = git.find_git_project_root()
    cfg_search_paths = [Path(".")]
    if git_project_root:
        cfg_search_paths.append(git_project_root)

    for path in cfg_search_paths:
        for filename in defaults.CONFIG_FILES:
            out_path = path / Path(filename)
            if out_path.exists():
                yield out_path


def read_cfg(filepath: str | None = None) -> BaseConfig:
    for filename in _resolve_config_paths(filepath):
        with open(filename, "rb") as f:
            data: bytes = f.read()

        conf = create_config(data=data, path=filename)
        if not conf.is_empty_config:
            return conf

        if filepath is not None:
            raise ConfigFileIsEmpty()

    return BaseConfig()
