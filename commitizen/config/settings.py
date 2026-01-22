from collections import ChainMap
from collections.abc import Mapping
from typing import Any, cast

from commitizen.defaults import DEFAULT_SETTINGS, Settings


class ChainSettings:
    def __init__(
        self,
        config_file_settings: Mapping[str, Any],
        cli_settings: Mapping[str, Any] | None = None,
    ) -> None:
        if cli_settings is None:
            cli_settings = {}
        self._chain_map: ChainMap[str, Any] = ChainMap[Any, Any](
            self._remove_none_values(cli_settings),
            self._remove_none_values(config_file_settings),
            DEFAULT_SETTINGS,  # type: ignore[arg-type]
        )

    def load_settings(self) -> Settings:
        return cast("Settings", dict(self._chain_map))

    def _remove_none_values(self, settings: Mapping[str, Any]) -> dict[str, Any]:
        """HACK: remove None values from settings to avoid incorrectly overriding settings."""
        return {k: v for k, v in settings.items() if v is not None}
