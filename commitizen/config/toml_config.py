from __future__ import annotations

from typing import TYPE_CHECKING, Any

from tomlkit import TOMLDocument, exceptions, parse, table

from .base_config import BaseConfig

if TYPE_CHECKING:
    import sys
    from pathlib import Path

    # Self is Python 3.11+ but backported in typing-extensions
    if sys.version_info < (3, 11):
        from typing_extensions import Self
    else:
        from typing import Self


class TomlConfig(BaseConfig):
    _parse_errors = (exceptions.ParseError,)
    _missing_section_errors = (exceptions.NonExistentKey,)

    def __init__(self, *, data: bytes | str, path: Path) -> None:
        super().__init__()
        self.path = path
        self._parse_setting(data)

    def contains_commitizen_section(self) -> bool:
        config_doc = parse(self.path.read_bytes())
        return config_doc.get("tool", {}).get("commitizen") is not None

    def init_empty_config_content(self) -> None:
        config_doc = TOMLDocument()
        if self.path.is_file():
            config_doc = parse(self.path.read_bytes())

        if config_doc.get("tool") is None:
            config_doc["tool"] = table()
        config_doc["tool"]["commitizen"] = table()  # type: ignore[index]

        with self.path.open("wb") as output_toml_file:
            output_toml_file.write(
                config_doc.as_string().encode(self._settings["encoding"])
            )

    def set_key(self, key: str, value: object) -> Self:
        config_doc = parse(self.path.read_bytes())

        config_doc["tool"]["commitizen"][key] = value  # type: ignore[index]
        self.path.write_bytes(config_doc.as_string().encode(self._settings["encoding"]))

        return self

    def _load_document(self, data: bytes | str) -> Any:
        """We expect to have a section in pyproject looking like

        ```
        [tool.commitizen]
        name = "cz_conventional_commits"
        ```
        """
        return parse(data)

    def _get_commitizen_section(self, doc: Any) -> Any:
        return doc["tool"]["commitizen"]
