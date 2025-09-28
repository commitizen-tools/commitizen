from __future__ import annotations

import pytest

from commitizen import defaults
from commitizen.changelog_formats import (
    KNOWN_CHANGELOG_FORMATS,
    ChangelogFormat,
    _guess_changelog_format,
    get_changelog_format,
)
from commitizen.config.base_config import BaseConfig
from commitizen.exceptions import ChangelogFormatUnknown


@pytest.mark.parametrize("format", KNOWN_CHANGELOG_FORMATS.values())
def test_guess_format(format: type[ChangelogFormat]):
    assert _guess_changelog_format(f"CHANGELOG.{format.extension}") is format
    for ext in format.alternative_extensions:
        assert _guess_changelog_format(f"CHANGELOG.{ext}") is format


@pytest.mark.parametrize("filename", ("CHANGELOG", "NEWS", "file.unknown", None))
def test_guess_format_unknown(filename: str):
    assert _guess_changelog_format(filename) is None


@pytest.mark.parametrize(
    "name, expected",
    [
        pytest.param(name, format, id=name)
        for name, format in KNOWN_CHANGELOG_FORMATS.items()
    ],
)
def test_get_format(
    mock_config: BaseConfig, name: str, expected: type[ChangelogFormat]
):
    mock_config.settings["changelog_format"] = name
    assert isinstance(get_changelog_format(mock_config), expected)


@pytest.mark.parametrize("filename", (None, ""))
def test_get_format_empty_filename(mock_config: BaseConfig, filename: str | None):
    mock_config.settings["changelog_format"] = defaults.CHANGELOG_FORMAT
    assert isinstance(
        get_changelog_format(mock_config, filename),
        KNOWN_CHANGELOG_FORMATS[defaults.CHANGELOG_FORMAT],
    )


@pytest.mark.parametrize("filename", (None, ""))
def test_get_format_empty_filename_no_setting(
    mock_config: BaseConfig, filename: str | None
):
    mock_config.settings["changelog_format"] = None
    with pytest.raises(ChangelogFormatUnknown):
        get_changelog_format(mock_config, filename)


@pytest.mark.parametrize("filename", ("extensionless", "file.unknown"))
def test_get_format_unknown(mock_config: BaseConfig, filename: str | None):
    with pytest.raises(ChangelogFormatUnknown):
        get_changelog_format(mock_config, filename)
