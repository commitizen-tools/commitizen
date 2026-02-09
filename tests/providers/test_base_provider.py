from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from commitizen.exceptions import VersionProviderUnknown
from commitizen.providers import get_provider
from commitizen.providers.commitizen_provider import CommitizenProvider
from commitizen.providers.composer_provider import ComposerProvider
from commitizen.providers.pep621_provider import Pep621Provider
from commitizen.providers.uv_provider import UvProvider

if TYPE_CHECKING:
    from pathlib import Path

    from commitizen.config.base_config import BaseConfig


def test_default_version_provider_is_commitizen_config(config: BaseConfig):
    provider = get_provider(config)

    assert isinstance(provider, CommitizenProvider)


def test_raise_for_unknown_provider(config: BaseConfig):
    config.settings["version_provider"] = "unknown"
    with pytest.raises(VersionProviderUnknown):
        get_provider(config)


@pytest.mark.parametrize("encoding", ["utf-8", "latin-1"])
def test_file_provider_get_encoding(config: BaseConfig, encoding: str):
    """_get_encoding should return the configured encoding."""
    config.settings["encoding"] = encoding
    provider = ComposerProvider(config)
    assert provider._get_encoding() == encoding


def test_json_provider_uses_encoding_with_encoding_fixture(
    config: BaseConfig,
    chdir: Path,
    data_dir: Path,
):
    """JsonProvider should correctly read a JSON file with non-ASCII content."""
    source = data_dir / "encoding_test_composer.json"
    target = chdir / "composer.json"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    config.settings["encoding"] = "utf-8"
    config.settings["version_provider"] = "composer"

    provider = get_provider(config)
    assert isinstance(provider, ComposerProvider)
    assert provider.get_version() == "0.1.0"


def test_toml_provider_uses_encoding_with_encoding_fixture(
    config: BaseConfig,
    chdir: Path,
    data_dir: Path,
):
    """TomlProvider should correctly read a TOML file with non-ASCII content."""
    source = data_dir / "encoding_test_pyproject.toml"
    target = chdir / "pyproject.toml"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    config.settings["encoding"] = "utf-8"
    config.settings["version_provider"] = "uv"

    provider = get_provider(config)
    assert isinstance(provider, UvProvider)
    assert provider.get_version() == "0.4.1"


def test_json_provider_set_version_uses_encoding_with_encoding_fixture(
    config: BaseConfig,
    chdir: Path,
    data_dir: Path,
):
    """JsonProvider.set_version should correctly write a JSON file with non-ASCII content."""
    source = data_dir / "encoding_test_composer.json"
    target = chdir / "composer.json"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    config.settings["encoding"] = "utf-8"
    config.settings["version_provider"] = "composer"

    provider = get_provider(config)
    assert isinstance(provider, ComposerProvider)
    
    # Update version using set_version
    provider.set_version("1.0.0")
    
    # Verify the file can be read back with the same encoding
    assert provider.get_version() == "1.0.0"
    
    # Verify the non-ASCII content is preserved
    content = target.read_text(encoding="utf-8")
    assert "Тест описания для проверки кодировки" in content


def test_json_provider_handles_various_unicode_characters(
    config: BaseConfig,
    chdir: Path,
):
    """JsonProvider should handle a wide range of Unicode characters."""
    config.settings["encoding"] = "utf-8"
    config.settings["version_provider"] = "composer"

    filename = ComposerProvider.filename
    file = chdir / filename
    file.write_text(
        (
            "{\n"
            '  "name": "多言語-имя-árbol",\n'
            '  "description": "Emoji 😀 – 漢字 – العربية",\n'
            '  "version": "0.1.0"\n'
            "}\n"
        ),
        encoding="utf-8",
    )

    provider = get_provider(config)
    assert isinstance(provider, ComposerProvider)
    assert provider.get_version() == "0.1.0"


def test_toml_provider_set_version_uses_encoding_with_encoding_fixture(
    config: BaseConfig,
    chdir: Path,
    data_dir: Path,
):
    """TomlProvider.set_version should correctly write a TOML file with non-ASCII content."""
    source = data_dir / "encoding_test_pyproject.toml"
    target = chdir / "pyproject.toml"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    config.settings["encoding"] = "utf-8"
    config.settings["version_provider"] = "pep621"

    provider = get_provider(config)
    assert isinstance(provider, Pep621Provider)
    
    # Update version using set_version
    provider.set_version("1.0.0")
    
    # Verify the file can be read back with the same encoding
    assert provider.get_version() == "1.0.0"
    
    # Verify the non-ASCII content is preserved
    content = target.read_text(encoding="utf-8")
    assert "Новое" in content
    assert "Исправление" in content
    assert "Выберите тип изменений" in content


def test_toml_provider_handles_various_unicode_characters(
    config: BaseConfig,
    chdir: Path,
):
    """TomlProvider should handle a wide range of Unicode characters."""
    config.settings["encoding"] = "utf-8"
    config.settings["version_provider"] = "pep621"

    filename = Pep621Provider.filename
    file = chdir / filename
    file.write_text(
        (
            "[project]\n"
            'name = "多言語-имя-árbol"\n'
            'description = "Emoji 😀 – 漢字 – العربية"\n'
            'version = "0.1.0"\n'
        ),
        encoding="utf-8",
    )

    provider = get_provider(config)
    assert isinstance(provider, Pep621Provider)
    assert provider.get_version() == "0.1.0"
