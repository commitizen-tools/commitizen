from __future__ import annotations

from typing import TYPE_CHECKING

from commitizen.config.json_config import JsonConfig
from commitizen.config.toml_config import TomlConfig
from commitizen.config.yaml_config import YAMLConfig

if TYPE_CHECKING:
    from pathlib import Path

    from commitizen.config.base_config import BaseConfig


def create_config(*, data: bytes | str | None = None, path: Path) -> BaseConfig:
    if "toml" in path.suffix:
        return TomlConfig(data=data or "", path=path)
    if "json" in path.suffix:
        return JsonConfig(data=data or "{}", path=path)
    if "yaml" in path.suffix:
        return YAMLConfig(data=data or "", path=path)

    # Should be unreachable. See the constant CONFIG_FILES.
    raise ValueError(
        f"Unsupported config file: {path.name} due to unknown file extension"
    )
