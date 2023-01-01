from __future__ import annotations

import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Iterator, Optional

import pytest

from commitizen.config.base_config import BaseConfig
from commitizen.exceptions import VersionProviderUnknown
from commitizen.providers import (
    CargoProvider,
    CommitizenProvider,
    ComposerProvider,
    NpmProvider,
    Pep621Provider,
    PoetryProvider,
    ScmProvider,
    get_provider,
)
from tests.utils import create_file_and_commit, create_tag

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


def test_npm_provider(config: BaseConfig, chdir: Path):
    package_json = chdir / "package.json"
    package_json.write_text(
        dedent(
            """\
            {
              "name": "whatever",
              "version": "0.1.0"
            }
            """
        )
    )
    config.settings["version_provider"] = "npm"

    provider = get_provider(config)
    assert isinstance(provider, NpmProvider)
    assert provider.get_version() == "0.1.0"

    provider.set_version("43.1")
    assert package_json.read_text() == dedent(
        """\
        {
          "name": "whatever",
          "version": "43.1"
        }
        """
    )


def test_composer_provider(config: BaseConfig, chdir: Path):
    composer_json = chdir / "composer.json"
    composer_json.write_text(
        dedent(
            """\
            {
                "name": "whatever",
                "version": "0.1.0"
            }
            """
        )
    )
    config.settings["version_provider"] = "composer"

    provider = get_provider(config)
    assert isinstance(provider, ComposerProvider)
    assert provider.get_version() == "0.1.0"

    provider.set_version("43.1")
    assert composer_json.read_text() == dedent(
        """\
        {
            "name": "whatever",
            "version": "43.1"
        }
        """
    )


@pytest.mark.parametrize(
    "tag_format,tag,version",
    (
        (None, "0.1.0", "0.1.0"),
        (None, "v0.1.0", "0.1.0"),
        ("v$version", "v0.1.0", "0.1.0"),
        ("version-$version", "version-0.1.0", "0.1.0"),
        ("version-$version", "version-0.1", "0.1"),
        ("version-$version", "version-0.1.0rc1", "0.1.0rc1"),
        ("v$minor.$major.$patch", "v1.0.0", "0.1.0"),
        ("version-$major.$minor.$patch", "version-0.1.0", "0.1.0"),
        ("v$major.$minor$prerelease$devrelease", "v1.0rc1", "1.0rc1"),
        ("v$major.$minor.$patch$prerelease$devrelease", "v0.1.0", "0.1.0"),
        ("v$major.$minor.$patch$prerelease$devrelease", "v0.1.0rc1", "0.1.0rc1"),
        ("v$major.$minor.$patch$prerelease$devrelease", "v1.0.0.dev0", "1.0.0.dev0"),
    ),
)
@pytest.mark.usefixtures("tmp_git_project")
def test_scm_provider(
    config: BaseConfig, tag_format: Optional[str], tag: str, version: str
):
    create_file_and_commit("test: fake commit")
    create_tag(tag)
    create_file_and_commit("test: fake commit")
    create_tag("should-not-match")

    config.settings["version_provider"] = "scm"
    config.settings["tag_format"] = tag_format

    provider = get_provider(config)
    assert isinstance(provider, ScmProvider)
    assert provider.get_version() == version

    # Should not fail on set_version()
    provider.set_version("43.1")


@pytest.mark.usefixtures("tmp_git_project")
def test_scm_provider_default_without_matching_tag(config: BaseConfig):
    create_file_and_commit("test: fake commit")
    create_tag("should-not-match")
    create_file_and_commit("test: fake commit")

    config.settings["version_provider"] = "scm"

    provider = get_provider(config)
    assert isinstance(provider, ScmProvider)
    assert provider.get_version() == "0.0.0"


@pytest.mark.usefixtures("tmp_git_project")
def test_scm_provider_default_without_commits_and_tags(config: BaseConfig):
    config.settings["version_provider"] = "scm"

    provider = get_provider(config)
    assert isinstance(provider, ScmProvider)
    assert provider.get_version() == "0.0.0"
