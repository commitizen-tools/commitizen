from __future__ import annotations

from pathlib import Path

from commitizen import defaults, git, out
from commitizen.config.factory import create_config
from commitizen.exceptions import ConfigFileIsEmpty, ConfigFileNotFound

from .base_config import BaseConfig


def _resolve_config_candidates() -> list[BaseConfig]:
    git_project_root = git.find_git_project_root()
    cfg_search_paths = [Path(".")]

    if git_project_root and cfg_search_paths[0].resolve() != git_project_root.resolve():
        cfg_search_paths.append(git_project_root)

    candidates: list[BaseConfig] = []
    for dir in cfg_search_paths:
        for filename in defaults.CONFIG_FILES:
            out_path = dir / filename
            if out_path.is_file():
                conf = _create_config_from_path(out_path)
                if conf.contains_commitizen_section():
                    candidates.append(conf)
    return candidates


def _create_config_from_path(path: Path) -> BaseConfig:
    with path.open("rb") as f:
        return create_config(data=f.read(), path=path)


def read_cfg(filepath: str | None = None) -> BaseConfig:
    if filepath is not None:
        conf_path = Path(filepath)
        if not conf_path.is_file():
            raise ConfigFileNotFound()
        conf = _create_config_from_path(conf_path)
        if not conf.contains_commitizen_section():
            raise ConfigFileIsEmpty()
        return conf

    config_candidates = _resolve_config_candidates()
    if len(config_candidates) > 1:
        out.warn(
            f"Multiple config files detected: {', '.join(str(conf.path) for conf in config_candidates)}. "
            f"Using config file: '{config_candidates[0].path}'."
        )

    return config_candidates[0] if config_candidates else BaseConfig()
