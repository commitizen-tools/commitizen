"""Tests for explicit UTF-8 encoding in file read/write operations.

Reproduces the issue from #1636 where on Windows, Path.read_text() and
Path.write_text() default to the system encoding (e.g. CP1251) rather than
UTF-8, causing UnicodeDecodeError when files contain non-ASCII characters
such as Cyrillic text in commitizen customize options.

The tests monkeypatch Path.read_text/write_text to simulate Windows behavior
by raising UnicodeDecodeError when encoding is not explicitly specified.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
import tomlkit

from commitizen.providers import get_provider
from commitizen.providers.cargo_provider import CargoProvider
from commitizen.providers.npm_provider import NpmProvider
from commitizen.providers.pep621_provider import Pep621Provider
from commitizen.providers.uv_provider import UvProvider

if TYPE_CHECKING:
    from commitizen.config.base_config import BaseConfig

# Non-ASCII content for testing: Cyrillic, Chinese, accented characters
NON_ASCII_COMMENT = "# Тестовый комментарий 测试注释 cafe\u0301"

PEP621_TOML_WITH_NON_ASCII = """\
[project]
name = "my-project"
version = "0.1.0"
description = "Описание проекта 项目描述"
"""

PEP621_TOML_EXPECTED = """\
[project]
name = "my-project"
version = "42.1"
description = "Описание проекта 项目描述"
"""

NPM_PACKAGE_WITH_NON_ASCII = """\
{
  "name": "my-project",
  "version": "0.1.0",
  "description": "Описание проекта 项目描述"
}
"""

NPM_PACKAGE_EXPECTED = """\
{
  "name": "my-project",
  "version": "42.1",
  "description": "\\u041e\\u043f\\u0438\\u0441\\u0430\\u043d\\u0438\\u0435 \\u043f\\u0440\\u043e\\u0435\\u043a\\u0442\\u0430 \\u9879\\u76ee\\u63cf\\u8ff0"
}
"""

CARGO_TOML_WITH_NON_ASCII = """\
[package]
name = "whatever"
version = "0.1.0"
description = "Описание проекта 项目描述"
"""

UV_PYPROJECT_WITH_NON_ASCII = """\
[project]
name = "test-uv"
version = "4.2.1"
description = "Описание проекта 项目描述"
"""

UV_LOCK_WITH_NON_ASCII = """\
version = 1
revision = 1
requires-python = ">=3.13"

[[package]]
name = "test-uv"
version = "4.2.1"
source = { virtual = "." }
"""


def _make_strict_read_text(original_read_text):
    """Wrap Path.read_text to raise UnicodeDecodeError when encoding is not
    explicitly set, simulating Windows with a non-UTF-8 default encoding
    (e.g. CP1251)."""

    def strict_read_text(self, *args, encoding=None, errors=None):
        if encoding is None:
            raise UnicodeDecodeError(
                "charmap",
                b"\x98",
                0,
                1,
                "character maps to <undefined>",
            )
        return original_read_text(self, *args, encoding=encoding, errors=errors)

    return strict_read_text


def _make_strict_write_text(original_write_text):
    """Wrap Path.write_text to raise UnicodeEncodeError when encoding is not
    explicitly set, simulating Windows with a non-UTF-8 default encoding."""

    def strict_write_text(self, data, *args, encoding=None, errors=None, **kwargs):
        if encoding is None:
            raise UnicodeEncodeError(
                "charmap",
                data if isinstance(data, str) else "",
                0,
                1,
                "character maps to <undefined>",
            )
        return original_write_text(
            self, data, *args, encoding=encoding, errors=errors, **kwargs
        )

    return strict_write_text


@pytest.fixture
def _simulate_non_utf8_locale():
    """Simulate a Windows environment where the default filesystem encoding
    is not UTF-8 by monkeypatching Path.read_text and Path.write_text.

    When encoding is not explicitly passed, these methods will raise
    UnicodeDecodeError / UnicodeEncodeError, reproducing the behavior
    described in issue #1636.
    """
    original_read_text = Path.read_text
    original_write_text = Path.write_text

    with (
        patch.object(Path, "read_text", _make_strict_read_text(original_read_text)),
        patch.object(Path, "write_text", _make_strict_write_text(original_write_text)),
    ):
        yield


class TestPep621ProviderUtf8:
    """Test that Pep621Provider (TomlProvider) handles non-ASCII content."""

    @pytest.mark.usefixtures("_simulate_non_utf8_locale")
    def test_get_version_with_non_ascii_content(self, config: BaseConfig, chdir: Path):
        file = chdir / Pep621Provider.filename
        file.write_text(PEP621_TOML_WITH_NON_ASCII, encoding="utf-8")
        config.settings["version_provider"] = "pep621"

        provider = get_provider(config)
        assert isinstance(provider, Pep621Provider)
        assert provider.get_version() == "0.1.0"

    @pytest.mark.usefixtures("_simulate_non_utf8_locale")
    def test_set_version_with_non_ascii_content(self, config: BaseConfig, chdir: Path):
        file = chdir / Pep621Provider.filename
        file.write_text(PEP621_TOML_WITH_NON_ASCII, encoding="utf-8")
        config.settings["version_provider"] = "pep621"

        provider = get_provider(config)
        provider.set_version("42.1")

        result = file.read_text(encoding="utf-8")
        assert result == PEP621_TOML_EXPECTED

    @pytest.mark.usefixtures("_simulate_non_utf8_locale")
    def test_roundtrip_preserves_non_ascii(self, config: BaseConfig, chdir: Path):
        """Verify non-ASCII characters survive a read-modify-write cycle."""
        file = chdir / Pep621Provider.filename
        file.write_text(PEP621_TOML_WITH_NON_ASCII, encoding="utf-8")
        config.settings["version_provider"] = "pep621"

        provider = get_provider(config)
        provider.set_version("42.1")
        result = file.read_text(encoding="utf-8")

        assert "Описание проекта" in result
        assert "项目描述" in result


class TestNpmProviderUtf8:
    """Test that NpmProvider handles non-ASCII content."""

    @pytest.mark.usefixtures("_simulate_non_utf8_locale")
    def test_get_version_with_non_ascii_content(self, config: BaseConfig, chdir: Path):
        pkg = chdir / NpmProvider.package_filename
        pkg.write_text(NPM_PACKAGE_WITH_NON_ASCII, encoding="utf-8")
        config.settings["version_provider"] = "npm"

        provider = get_provider(config)
        assert isinstance(provider, NpmProvider)
        assert provider.get_version() == "0.1.0"

    @pytest.mark.usefixtures("_simulate_non_utf8_locale")
    def test_set_version_with_non_ascii_content(self, config: BaseConfig, chdir: Path):
        pkg = chdir / NpmProvider.package_filename
        pkg.write_text(NPM_PACKAGE_WITH_NON_ASCII, encoding="utf-8")
        config.settings["version_provider"] = "npm"

        provider = get_provider(config)
        provider.set_version("42.1")

        result = json.loads(pkg.read_text(encoding="utf-8"))
        assert result["version"] == "42.1"


class TestCargoProviderUtf8:
    """Test that CargoProvider handles non-ASCII content."""

    @pytest.mark.usefixtures("_simulate_non_utf8_locale")
    def test_get_version_with_non_ascii_content(self, config: BaseConfig, chdir: Path):
        file = chdir / CargoProvider.filename
        file.write_text(CARGO_TOML_WITH_NON_ASCII, encoding="utf-8")
        config.settings["version_provider"] = "cargo"

        provider = get_provider(config)
        assert isinstance(provider, CargoProvider)
        assert provider.get_version() == "0.1.0"

    @pytest.mark.usefixtures("_simulate_non_utf8_locale")
    def test_set_version_with_non_ascii_content(self, config: BaseConfig, chdir: Path):
        file = chdir / CargoProvider.filename
        file.write_text(CARGO_TOML_WITH_NON_ASCII, encoding="utf-8")
        config.settings["version_provider"] = "cargo"

        provider = get_provider(config)
        provider.set_version("42.1")

        result = file.read_text(encoding="utf-8")
        doc = tomlkit.parse(result)
        assert doc["package"]["version"] == "42.1"
        assert "Описание проекта" in result


class TestUvProviderUtf8:
    """Test that UvProvider handles non-ASCII content."""

    @pytest.mark.usefixtures("_simulate_non_utf8_locale")
    def test_get_version_with_non_ascii_content(self, config: BaseConfig, chdir: Path):
        pyproject_file = chdir / UvProvider.filename
        pyproject_file.write_text(UV_PYPROJECT_WITH_NON_ASCII, encoding="utf-8")
        uv_lock_file = chdir / UvProvider.lock_filename
        uv_lock_file.write_text(UV_LOCK_WITH_NON_ASCII, encoding="utf-8")
        config.settings["version_provider"] = "uv"

        provider = get_provider(config)
        assert isinstance(provider, UvProvider)
        assert provider.get_version() == "4.2.1"

    @pytest.mark.usefixtures("_simulate_non_utf8_locale")
    def test_set_version_with_non_ascii_content(self, config: BaseConfig, chdir: Path):
        pyproject_file = chdir / UvProvider.filename
        pyproject_file.write_text(UV_PYPROJECT_WITH_NON_ASCII, encoding="utf-8")
        uv_lock_file = chdir / UvProvider.lock_filename
        uv_lock_file.write_text(UV_LOCK_WITH_NON_ASCII, encoding="utf-8")
        config.settings["version_provider"] = "uv"

        provider = get_provider(config)
        provider.set_version("100.0.0")

        pyproject_result = pyproject_file.read_text(encoding="utf-8")
        assert "100.0.0" in pyproject_result
        assert "Описание проекта" in pyproject_result

        lock_result = uv_lock_file.read_text(encoding="utf-8")
        assert "100.0.0" in lock_result
