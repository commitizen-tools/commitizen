from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from commitizen.defaults import DEFAULT_SETTINGS, Settings

if TYPE_CHECKING:
    import sys

    # Self is Python 3.11+ but backported in typing-extensions
    if sys.version_info < (3, 11):
        from typing_extensions import Self
    else:
        from typing import Self


class BaseConfig:
    def __init__(self) -> None:
        self._settings: Settings = DEFAULT_SETTINGS.copy()
        self.encoding = self.settings["encoding"]
        self._path: Path | None = None

    @property
    def settings(self) -> Settings:
        return self._settings

    @property
    def path(self) -> Path:
        return self._path  # type: ignore[return-value]

    @path.setter
    def path(self, path: str | Path) -> None:
        self._path = Path(path)

    def set_key(self, key: str, value: Any) -> Self:
        """Set or update a key in the conf.

        For now only strings are supported.
        We use to update the version number.
        """
        raise NotImplementedError()

    def update(self, data: Settings) -> None:
        self._settings.update(data)

    def _parse_setting(self, data: bytes | str) -> None:
        raise NotImplementedError()

    def init_empty_config_content(self) -> None:
        raise NotImplementedError()
