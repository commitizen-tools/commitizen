from typing import Optional

from commitizen.defaults import DEFAULT_SETTINGS


class BaseConfig:
    def __init__(self):
        self._settings: dict = DEFAULT_SETTINGS.copy()
        self._path: Optional[str] = None

    @property
    def settings(self) -> dict:
        return self._settings

    @property
    def path(self) -> str:
        return self._path

    def set_key(self, key, value):
        """Set or update a key in the conf.

        For now only strings are supported.
        We use to update the version number.
        """
        return self

    def update(self, data: dict):
        self._settings.update(data)

    def add_path(self, path: str):
        self._path = path

    def _parse_setting(self, data: str) -> dict:
        raise NotImplementedError()
