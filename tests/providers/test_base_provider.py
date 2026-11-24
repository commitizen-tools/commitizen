from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from commitizen import cmd
from commitizen.exceptions import VersionProviderUnknown
from commitizen.providers import get_provider
from commitizen.providers.cargo_provider import CargoProvider
from commitizen.providers.commitizen_provider import CommitizenProvider
from commitizen.providers.composer_provider import ComposerProvider
from commitizen.providers.npm_provider import NpmProvider
from commitizen.providers.pep621_provider import Pep621Provider
from commitizen.providers.poetry_provider import PoetryProvider
from commitizen.providers.uv_provider import UvProvider

if TYPE_CHECKING:
    from pathlib import Path

    from commitizen.config.base_config import BaseConfig
    from commitizen.providers.base_provider import FileProvider


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


PYPROJECT_TOML = '[project]\nname = "demo"\nversion = "0.1.0"\n'
POETRY_TOML = '[tool.poetry]\nname = "demo"\nversion = "0.1.0"\n'
UV_LOCK = 'version = 1\n\n[[package]]\nname = "demo"\nversion = "0.1.0"\n'
CARGO_TOML = '[package]\nname = "demo"\nversion = "0.1.0"\n'
CARGO_LOCK = 'version = 3\n\n[[package]]\nname = "demo"\nversion = "0.1.0"\n'
PACKAGE_JSON = '{\n  "name": "demo",\n  "version": "0.1.0"\n}\n'
COMPOSER_JSON = '{\n    "name": "demo",\n    "version": "0.1.0"\n}\n'
PACKAGE_LOCK_JSON = """\
{
  "name": "demo",
  "version": "0.1.0",
  "packages": {
    "": {
      "name": "demo",
      "version": "0.1.0"
    }
  }
}
"""


@pytest.mark.parametrize("eol", ["lf", "crlf"])
@pytest.mark.parametrize(
    ("provider_cls", "files"),
    [
        pytest.param(Pep621Provider, {"pyproject.toml": PYPROJECT_TOML}, id="pep621"),
        pytest.param(PoetryProvider, {"pyproject.toml": POETRY_TOML}, id="poetry"),
        pytest.param(
            UvProvider,
            {"pyproject.toml": PYPROJECT_TOML, "uv.lock": UV_LOCK},
            id="uv",
        ),
        pytest.param(
            CargoProvider,
            {"Cargo.toml": CARGO_TOML, "Cargo.lock": CARGO_LOCK},
            id="cargo",
        ),
        pytest.param(ComposerProvider, {"composer.json": COMPOSER_JSON}, id="composer"),
        pytest.param(
            NpmProvider,
            {
                "package.json": PACKAGE_JSON,
                "package-lock.json": PACKAGE_LOCK_JSON,
                "npm-shrinkwrap.json": PACKAGE_LOCK_JSON,
            },
            id="npm",
        ),
    ],
)
def test_file_provider_writes_git_core_eol(
    config: BaseConfig,
    tmp_git_project: Path,
    provider_cls: type[FileProvider],
    files: dict[str, str],
    eol: str,
):
    """File providers write the line ending set by `git config core.eol`.

    `version_files` and the changelog already follow `core.eol`. Without this,
    `cz bump` on Windows with `core.eol=lf` rewrote `pyproject.toml` with CRLF.
    """
    # Arrange
    newline = "\r\n" if eol == "crlf" else "\n"
    for filename, content in files.items():
        (tmp_git_project / filename).write_bytes(
            content.replace("\n", newline).encode()
        )
    cmd.run(["git", "config", "core.eol", eol])

    # Act
    provider_cls(config).set_version("0.2.0")

    # Assert
    for filename, content in files.items():
        expected = content.replace("0.1.0", "0.2.0").replace("\n", newline)
        assert (tmp_git_project / filename).read_bytes() == expected.encode()
