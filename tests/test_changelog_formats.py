from __future__ import annotations
from typing import Optional

import pytest
from commitizen.config.base_config import BaseConfig
from commitizen.formats import (
    DEFAULT_FORMAT,
    KNOWN_FORMATS,
    Format,
    get_format,
    guess_format,
)
from commitizen.formats.errors import FormatUnknown


@pytest.mark.parametrize("format", KNOWN_FORMATS.values())
def test_guess_format(format: type[Format]):
    assert guess_format(f"CHANGELOG.{format.extension}") is format
    for ext in format.alternative_extensions:
        assert guess_format(f"CHANGELOG.{ext}") is format


@pytest.mark.parametrize("filename", ("CHANGELOG", "NEWS", "file.unknown", None))
def test_guess_format_unknown(filename: str):
    assert guess_format(filename) is None


@pytest.mark.parametrize(
    "name, expected",
    [pytest.param(name, format, id=name) for name, format in KNOWN_FORMATS.items()],
)
def test_get_format(config: BaseConfig, name: str, expected: type[Format]):
    config.settings["format"] = name
    assert isinstance(get_format(config), expected)


@pytest.mark.parametrize("filename", (None, ""))
def test_get_format_empty_filename(config: BaseConfig, filename: Optional[str]):
    config.settings["format"] = DEFAULT_FORMAT
    assert isinstance(get_format(config, filename), KNOWN_FORMATS[DEFAULT_FORMAT])


@pytest.mark.parametrize("filename", (None, ""))
def test_get_format_empty_filename_no_setting(
    config: BaseConfig, filename: Optional[str]
):
    config.settings["format"] = None
    with pytest.raises(FormatUnknown):
        get_format(config, filename)


@pytest.mark.parametrize("filename", ("extensionless", "file.unknown"))
def test_get_format_unknown(config: BaseConfig, filename: Optional[str]):
    with pytest.raises(FormatUnknown):
        get_format(config, filename)
