from __future__ import annotations

import json
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

import tomlkit
import yaml

from commitizen import out

if TYPE_CHECKING:
    from commitizen.config import BaseConfig


class DumpConfig:
    """Output the current commitizen configuration."""

    def __init__(self, config: BaseConfig, arguments: dict[str, Any]) -> None:
        self.config: BaseConfig = config
        self.format: str = arguments.get("format", "toml")

    def __call__(self) -> None:
        settings = dict(self.config.settings)

        if self.format == "toml":
            filtered = _filter_none_values(settings)
            doc = tomlkit.document()
            tool_table = tomlkit.table()
            cz_table = tomlkit.table()
            for key, value in filtered.items():
                cz_table.add(key, value)
            tool_table.add("commitizen", cz_table)
            doc.add("tool", tool_table)
            out.write(tomlkit.dumps(doc))
        elif self.format == "yaml":
            out.write(
                yaml.safe_dump(
                    {"tool": {"commitizen": settings}},
                    default_flow_style=False,
                    allow_unicode=True,
                )
            )
        else:
            out.write(
                json.dumps({"tool": {"commitizen": settings}}, indent=2, default=str)
            )


def _filter_none_values(settings: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: _filter_none_values(value) if isinstance(value, Mapping) else value
        for key, value in settings.items()
        if value is not None
    }
