from __future__ import annotations

from pathlib import Path

from commitizen.defaults import DEFAULT_SETTINGS, Settings


class BaseConfig:
    def __init__(self):
        self._settings: Settings = DEFAULT_SETTINGS.copy()
        self.encoding = self.settings["encoding"]
        self._path: Path | None = None

    @property
    def settings(self) -> Settings:
        return self._settings

    @property
    def path(self) -> Path | None:
        return self._path

    def set_key(self, key, value):
        """Set or update a key in the conf.

        For now only strings are supported.
        We use to update the version number.
        """
        raise NotImplementedError()

    def update(self, data: Settings) -> None:
        self._settings.update(data)

    def add_path(self, path: str | Path) -> None:
        self._path = Path(path)

    def _parse_setting(self, data: bytes | str) -> None:
        raise NotImplementedError()
