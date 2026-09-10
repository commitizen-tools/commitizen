from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from commitizen import defaults
from commitizen.changelog_formats import (
    KNOWN_CHANGELOG_FORMATS,
    ChangelogFormat,
    _guess_changelog_format,
    get_changelog_format,
)
from commitizen.exceptions import ChangelogFormatUnknown

if TYPE_CHECKING:
    from commitizen.config.base_config import BaseConfig


@pytest.mark.parametrize("format", KNOWN_CHANGELOG_FORMATS.values())
def test_guess_format(format: type[ChangelogFormat]):
    assert _guess_changelog_format(f"CHANGELOG.{format.extension}") is format
    for ext in format.alternative_extensions:
        assert _guess_changelog_format(f"CHANGELOG.{ext}") is format


@pytest.mark.parametrize("filename", ["CHANGELOG", "NEWS", "file.unknown", None])
def test_guess_format_unknown(filename: str):
    assert _guess_changelog_format(filename) is None


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        pytest.param(name, format, id=name)
        for name, format in KNOWN_CHANGELOG_FORMATS.items()
    ],
)
def test_get_format(config: BaseConfig, name: str, expected: type[ChangelogFormat]):
    config.settings["changelog_format"] = name
    assert isinstance(get_changelog_format(config), expected)


@pytest.mark.parametrize("filename", [None, ""])
def test_get_format_empty_filename(config: BaseConfig, filename: str | None):
    config.settings["changelog_format"] = defaults.CHANGELOG_FORMAT
    assert isinstance(
        get_changelog_format(config, filename),
        KNOWN_CHANGELOG_FORMATS[defaults.CHANGELOG_FORMAT],
    )


@pytest.mark.parametrize("filename", [None, ""])
def test_get_format_empty_filename_no_setting(config: BaseConfig, filename: str | None):
    config.settings["changelog_format"] = None
    with pytest.raises(ChangelogFormatUnknown) as excinfo:
        get_changelog_format(config, filename)
    # The error message should hint at setting `changelog_format` and list
    # the known formats so users on non-standard file extensions know what
    # to do (#894).
    msg = str(excinfo.value)
    assert "changelog_format" in msg
    assert "Known formats" in msg


@pytest.mark.parametrize("filename", ["extensionless", "file.unknown"])
def test_get_format_unknown(config: BaseConfig, filename: str | None):
    with pytest.raises(ChangelogFormatUnknown) as excinfo:
        get_changelog_format(config, filename)
    # Same hint when the filename extension is unknown.
    msg = str(excinfo.value)
    assert "changelog_format" in msg
    assert "Known formats" in msg


def test_get_format_unknown_name_lists_known_formats(config: BaseConfig):
    """Regression test for #894: when ``changelog_format`` is set to an
    unknown value, the error must list the registered formats so users
    can self-correct."""
    config.settings["changelog_format"] = "definitely-not-a-format"
    with pytest.raises(ChangelogFormatUnknown) as excinfo:
        get_changelog_format(config)
    msg = str(excinfo.value)
    assert "definitely-not-a-format" in msg
    assert "Known formats" in msg


def test_get_format_unknown_name_with_known_filename_raises(config: BaseConfig):
    config.settings["changelog_format"] = "invalidformat"
    with pytest.raises(ChangelogFormatUnknown) as excinfo:
        get_changelog_format(config, "CHANGELOG.md")
    msg = str(excinfo.value)
    assert "invalidformat" in msg
    assert "Known formats" in msg
