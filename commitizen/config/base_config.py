from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from commitizen.defaults import DEFAULT_SETTINGS, Settings
from commitizen.exceptions import InvalidConfigurationError

if TYPE_CHECKING:
    import sys

    # Self is Python 3.11+ but backported in typing-extensions
    if sys.version_info < (3, 11):
        from typing_extensions import Self
    else:
        from typing import Self


class BaseConfig:
    _parse_errors: tuple[type[Exception], ...] = ()
    _missing_section_errors: tuple[type[Exception], ...] = ()

    def __init__(self) -> None:
        self._settings: Settings = DEFAULT_SETTINGS.copy()
        self._path: Path | None = None

    def contains_commitizen_section(self) -> bool:
        """Check if the config file contains a commitizen section.

        The implementation is different for each config file type.
        """
        raise NotImplementedError()

    @property
    def settings(self) -> Settings:
        return self._settings

    @property
    def path(self) -> Path:
        return self._path  # type: ignore[return-value]

    @path.setter
    def path(self, path: Path) -> None:
        self._path = Path(path)

    def set_key(self, key: str, value: object) -> Self:
        """Set or update a key in the config file.

        Currently, only strings are supported for the parameter key.
        """
        raise NotImplementedError()

    def update(self, data: Settings) -> None:
        self._settings.update(data)

    def _parse_setting(self, data: bytes | str) -> None:
        """Parse the config file and apply its commitizen section.

        A missing commitizen section is valid, the default settings stay.
        """
        try:
            doc = self._load_document(data)
        except self._parse_errors as e:
            raise InvalidConfigurationError(f"Failed to parse {self.path}: {e}")

        try:
            self.settings.update(self._get_commitizen_section(doc))
        except self._missing_section_errors:
            pass

    def _load_document(self, data: bytes | str) -> Any:
        """Parse the raw file content.

        The implementation is different for each config file type.
        """
        raise NotImplementedError()

    def _get_commitizen_section(self, doc: Any) -> Any:
        """Return the commitizen section of the parsed document.

        The implementation is different for each config file type.
        """
        raise NotImplementedError()

    def init_empty_config_content(self) -> None:
        """Create a config file with the empty config content.

        The implementation is different for each config file type.
        """
        raise NotImplementedError()
