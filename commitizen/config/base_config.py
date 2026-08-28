from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from commitizen.defaults import DEFAULT_SETTINGS, Settings
from commitizen.exceptions import InvalidConfigurationError

if TYPE_CHECKING:
    import sys
    from collections.abc import Iterable

    # Self is Python 3.11+ but backported in typing-extensions
    if sys.version_info < (3, 11):
        from typing_extensions import Self
    else:
        from typing import Self


# Top-level keys that may appear in the commitizen section of a
# configuration file. Derived from the Settings TypedDict plus
# ``annotated_tag_message``, which is read from settings but predates the
# TypedDict (see commitizen/commands/bump.py).
KNOWN_SETTINGS: frozenset[str] = frozenset(
    set(Settings.__required_keys__) | set(Settings.__optional_keys__)
) | frozenset({"annotated_tag_message"})


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

    def _check_unknown_keys(self, keys: Iterable[str]) -> None:
        """Raise when the configuration contains keys that are not known settings.

        Only enforced when the ``strict_config`` setting is enabled. Unknown
        top-level keys usually indicate a typo in the configuration file
        (e.g. ``bump_mesage``); silently ignoring them makes such mistakes
        hard to notice. Keys nested under ``customize`` and ``extras`` are
        plugin-owned and deliberately not checked.
        """
        if not self._settings.get("strict_config"):
            return

        unknown_keys = sorted(key for key in keys if key not in KNOWN_SETTINGS)
        if unknown_keys:
            raise InvalidConfigurationError(
                f"Unknown configuration key(s) in {self.path}: "
                f"{', '.join(unknown_keys)}. "
                "Check for typos in your configuration file."
            )

    def _parse_setting(self, data: bytes | str) -> None:
        raise NotImplementedError()

    def init_empty_config_content(self) -> None:
        """Create a config file with the empty config content.

        The implementation is different for each config file type.
        """
        raise NotImplementedError()
