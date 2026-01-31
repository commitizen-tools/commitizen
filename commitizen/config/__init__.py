from __future__ import annotations

from pathlib import Path

from commitizen import defaults, git, out
from commitizen.config.factory import create_config
from commitizen.exceptions import ConfigFileIsEmpty, ConfigFileNotFound

from .base_config import BaseConfig


def _resolve_config_candidates() -> list[BaseConfig]:
    git_project_root = git.find_git_project_root()
    cfg_search_paths = [Path(".")]

    if git_project_root and not cfg_search_paths[0].samefile(git_project_root):
        cfg_search_paths.append(git_project_root)

    # The following algorithm is ugly, but we need to ensure that the order of the candidates are preserved before v5.
    # Also, the number of possible config files is limited, so the complexity is not a problem.
    candidates: list[BaseConfig] = []
    for dir in cfg_search_paths:
        for filename in defaults.CONFIG_FILES:
            out_path = dir / Path(filename)
            if (
                out_path.exists()
                and not any(
                    out_path.samefile(candidate.path) for candidate in candidates
                )
                and not (conf := _create_config_from_path(out_path)).is_empty_config
            ):
                candidates.append(conf)
    return candidates


def _create_config_from_path(path: Path) -> BaseConfig:
    with open(path, "rb") as f:
        data: bytes = f.read()

    return create_config(data=data, path=path)


def read_cfg(filepath: str | None = None) -> BaseConfig:
    if filepath is not None:
        conf_path = Path(filepath)
        if not conf_path.exists():
            raise ConfigFileNotFound()
        conf = _create_config_from_path(conf_path)
        if conf.is_empty_config:
            raise ConfigFileIsEmpty()
        return conf

    config_candidates = _resolve_config_candidates()
    if len(config_candidates) > 1:
        out.warn(
            f"Multiple config files detected: {', '.join(str(conf.path) for conf in config_candidates)}. "
            f"Using config file: '{config_candidates[0].path}'."
        )

    return config_candidates[0] if config_candidates else BaseConfig()
