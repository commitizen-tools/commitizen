from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from commitizen import defaults, git, out
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


def _check_and_warn_multiple_configs(filepath: str | None = None) -> None:
    """Check if multiple config files exist and warn the user."""
    if filepath is not None:
        # If user explicitly specified a config file, no need to warn
        return

    git_project_root = git.find_git_project_root()
    cfg_search_paths = [Path(".")]
    if git_project_root:
        cfg_search_paths.append(git_project_root)

    for path in cfg_search_paths:
        # Find all existing config files (excluding pyproject.toml for clearer warning)
        existing_files = [
            filename
            for filename in defaults.CONFIG_FILES
            if filename != "pyproject.toml" and (path / filename).exists()
        ]

        # If more than one config file exists, warn the user
        if len(existing_files) > 1:
            # Find which one will be used (first non-empty one in the priority order)
            used_config = None
            for filename in defaults.CONFIG_FILES:
                config_path = path / filename
                if config_path.exists():
                    try:
                        with open(config_path, "rb") as f:
                            data = f.read()
                        conf = create_config(data=data, path=config_path)
                        if not conf.is_empty_config:
                            used_config = filename
                            break
                    except Exception:
                        continue

            if used_config:
                out.warn(
                    f"Multiple config files detected: {', '.join(existing_files)}. "
                    f"Using {used_config}."
                )
            break


def read_cfg(filepath: str | None = None) -> BaseConfig:
    _check_and_warn_multiple_configs(filepath)

    for filename in _resolve_config_paths(filepath):
        with open(filename, "rb") as f:
            data: bytes = f.read()

        conf = create_config(data=data, path=filename)
        if not conf.is_empty_config:
            return conf

        if filepath is not None:
            raise ConfigFileIsEmpty()

    return BaseConfig()
