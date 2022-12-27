from __future__ import annotations

import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Iterator

import pytest

from commitizen.config.base_config import BaseConfig
from commitizen.exceptions import VersionProviderUnknown
from commitizen.providers import (
    CargoProvider,
    CommitizenProvider,
    Pep621Provider,
    PoetryProvider,
    get_provider,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def chdir(tmp_path: Path) -> Iterator[Path]:
    cwd = Path()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(cwd)


def test_default_version_provider_is_commitizen_config(config: BaseConfig):
    provider = get_provider(config)

    assert isinstance(provider, CommitizenProvider)


def test_raise_for_unknown_provider(config: BaseConfig):
    config.settings["version_provider"] = "unknown"
    with pytest.raises(VersionProviderUnknown):
        get_provider(config)


def test_commitizen_provider(config: BaseConfig, mocker: MockerFixture):
    config.settings["version"] = "42"
    mock = mocker.patch.object(config, "set_key")

    provider = CommitizenProvider(config)
    assert provider.get_version() == "42"

    provider.set_version("43.1")
    mock.assert_called_once_with("version", "43.1")


def test_pep621_provider(config: BaseConfig, chdir: Path):
    pyproject_toml = chdir / "pyproject.toml"
    pyproject_toml.write_text(
        dedent(
            """\
            [project]
            version = "0.1.0"
            """
        )
    )

    provider = Pep621Provider(config)

    assert provider.get_version() == "0.1.0"

    provider.set_version("43.1")

    assert pyproject_toml.read_text() == dedent(
        """\
        [project]
        version = "43.1"
        """
    )


def test_poetry_provider(config: BaseConfig, chdir: Path):
    pyproject_toml = chdir / "pyproject.toml"
    pyproject_toml.write_text(
        dedent(
            """\
            [tool.poetry]
            version = "0.1.0"
            """
        )
    )
    config.settings["version_provider"] = "poetry"

    provider = get_provider(config)
    assert isinstance(provider, PoetryProvider)
    assert provider.get_version() == "0.1.0"

    provider.set_version("43.1")
    assert pyproject_toml.read_text() == dedent(
        """\
        [tool.poetry]
        version = "43.1"
        """
    )


def test_cargo_provider(config: BaseConfig, chdir: Path):
    cargo_toml = chdir / "Cargo.toml"
    cargo_toml.write_text(
        dedent(
            """\
            [package]
            version = "0.1.0"
            """
        )
    )
    config.settings["version_provider"] = "cargo"

    provider = get_provider(config)
    assert isinstance(provider, CargoProvider)
    assert provider.get_version() == "0.1.0"

    provider.set_version("43.1")
    assert cargo_toml.read_text() == dedent(
        """\
        [package]
        version = "43.1"
        """
    )
