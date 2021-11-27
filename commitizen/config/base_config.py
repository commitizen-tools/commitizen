from pathlib import Path
from typing import Optional, Union

from commitizen.defaults import DEFAULT_SETTINGS, Settings


class BaseConfig:
    def __init__(self):
        self._settings: Settings = DEFAULT_SETTINGS.copy()
        self._path: Optional[Path] = None

    @property
    def settings(self) -> Settings:
        return self._settings

    @property
    def path(self) -> Optional[Path]:
        return self._path

    def set_key(self, key, value):
        """Set or update a key in the conf.

        For now only strings are supported.
        We use to update the version number.
        """
        raise NotImplementedError()

    def update(self, data: Settings) -> None:
        self._settings.update(data)

    def add_path(self, path: Union[str, Path]) -> None:
        self._path = Path(path)

    def _parse_setting(self, data: Union[bytes, str]) -> None:
        raise NotImplementedError()
