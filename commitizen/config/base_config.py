from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from commitizen import out
from commitizen.defaults import DEFAULT_SETTINGS, KNOWN_SETTINGS_KEYS, Settings
from commitizen.exceptions import InvalidConfigurationError

if TYPE_CHECKING:
    import sys
    from collections.abc import Mapping

    # Self is Python 3.11+ but backported in typing-extensions
    if sys.version_info < (3, 11):
        from typing_extensions import Self
    else:
        from typing import Self


class BaseConfig:
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
        raise NotImplementedError()

    def _validate_known_keys(self, raw_settings: Mapping[str, Any]) -> None:
        """Detect unknown keys in the commitizen section of the config file.

        - When ``strict_config`` is ``True`` in ``raw_settings``, raise
          :class:`InvalidConfigurationError`.
        - Otherwise emit a warning so users notice typos without breaking back
          compatibility.
        """
        unknown_keys = sorted(k for k in raw_settings if k not in KNOWN_SETTINGS_KEYS)
        if not unknown_keys:
            return

        location = f" in '{self._path}'" if self._path is not None else ""
        keys_str = ", ".join(repr(k) for k in unknown_keys)
        plural = "keys" if len(unknown_keys) > 1 else "key"
        message = (
            f"Unknown commitizen configuration {plural}{location}: {keys_str}. "
            f"If this is intentional, move the value(s) under the 'extras' setting."
        )

        if bool(raw_settings.get("strict_config", False)):
            raise InvalidConfigurationError(message)
        out.warn(message)

    def init_empty_config_content(self) -> None:
        """Create a config file with the empty config content.

        The implementation is different for each config file type.
        """
        raise NotImplementedError()
