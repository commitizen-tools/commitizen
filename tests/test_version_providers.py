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
    ComposerProvider,
    NpmProvider,
    Npm2Provider,
    Pep621Provider,
    PoetryProvider,
    ScmProvider,
    VersionProvider,
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


FILE_PROVIDERS = [
    (
        "pep621",
        "pyproject.toml",
        Pep621Provider,
        """\
        [project]
        version = "0.1.0"
        """,
        """\
        [project]
        version = "42.1"
        """,
    ),
    (
        "poetry",
        "pyproject.toml",
        PoetryProvider,
        """\
        [tool.poetry]
        version = "0.1.0"
        """,
        """\
        [tool.poetry]
        version = "42.1"
        """,
    ),
    (
        "cargo",
        "Cargo.toml",
        CargoProvider,
        """\
        [workspace.package]
        version = "0.1.0"
        """,
        """\
        [workspace.package]
        version = "42.1"
        """,
    ),
    (
        "cargo",
        "Cargo.toml",
        CargoProvider,
        """\
        [package]
        version = "0.1.0"
        """,
        """\
        [package]
        version = "42.1"
        """,
    ),
    (
        "npm",
        "package.json",
        NpmProvider,
        """\
        {
          "name": "whatever",
          "version": "0.1.0"
        }
        """,
        """\
        {
          "name": "whatever",
          "version": "42.1"
        }
        """,
    ),
    (
        "composer",
        "composer.json",
        ComposerProvider,
        """\
        {
            "name": "whatever",
            "version": "0.1.0"
        }
        """,
        """\
        {
            "name": "whatever",
            "version": "42.1"
        }
        """,
    ),
]


@pytest.mark.parametrize(
    "id,filename,cls,content,expected",
    FILE_PROVIDERS,
)
def test_file_providers(
    config: BaseConfig,
    chdir: Path,
    id: str,
    filename: str,
    cls: type[VersionProvider],
    content: str,
    expected: str,
):
    file = chdir / filename
    file.write_text(dedent(content))
    config.settings["version_provider"] = id

    provider = get_provider(config)
    assert isinstance(provider, cls)
    assert provider.get_version() == "0.1.0"

    provider.set_version("42.1")
    assert file.read_text() == dedent(expected)


@pytest.mark.parametrize(
    "tag_format,tag,expected_version",
    (
        # If tag_format is $version (the default), version_scheme.parser is used.
        # Its DEFAULT_VERSION_PARSER allows a v prefix, but matches PEP440 otherwise.
        ("$version", "no-match-because-version-scheme-is-strict", "0.0.0"),
        ("$version", "0.1.0", "0.1.0"),
        ("$version", "v0.1.0", "0.1.0"),
        ("$version", "v-0.1.0", "0.0.0"),
        # If tag_format is not None or $version, TAG_FORMAT_REGEXS are used, which are
        # much more lenient but require a v prefix.
        ("v$version", "v0.1.0", "0.1.0"),
        ("v$version", "no-match-because-no-v-prefix", "0.0.0"),
        ("v$version", "v-match-TAG_FORMAT_REGEXS", "-match-TAG_FORMAT_REGEXS"),
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
    config: BaseConfig, tag_format: str, tag: str, expected_version: str
):
    create_file_and_commit("test: fake commit")
    create_tag(tag)
    create_file_and_commit("test: fake commit")
    create_tag("should-not-match")

    config.settings["version_provider"] = "scm"
    config.settings["tag_format"] = tag_format

    provider = get_provider(config)
    assert isinstance(provider, ScmProvider)
    actual_version = provider.get_version()
    assert actual_version == expected_version

    # Should not fail on set_version()
    provider.set_version("43.1")


@pytest.mark.usefixtures("tmp_git_project")
def test_scm_provider_default_without_commits_and_tags(config: BaseConfig):
    config.settings["version_provider"] = "scm"

    provider = get_provider(config)
    assert isinstance(provider, ScmProvider)
    assert provider.get_version() == "0.0.0"


NPM_PACKAGE_JSON = """\
{
  "name": "whatever",
  "version": "0.1.0"
}
"""

NPM_PACKAGE_EXPECTED = """\
{
  "name": "whatever",
  "version": "42.1"
}
"""

NPM_LOCKFILE_JSON = """\
{
  "name": "whatever",
  "version": "0.1.0",
  "lockfileVersion": 2,
  "requires": true,
  "packages": {
    "": {
      "name": "whatever",
      "version": "0.1.0"
    },
    "someotherpackage": {
      "version": "0.1.0"
    }
  }
}
"""

NPM_LOCKFILE_EXPECTED = """\
{
  "name": "whatever",
  "version": "42.1",
  "lockfileVersion": 2,
  "requires": true,
  "packages": {
    "": {
      "name": "whatever",
      "version": "42.1"
    },
    "someotherpackage": {
      "version": "0.1.0"
    }
  }
}
"""

NPM_NO_VERSION = """\
{
    "name": "whatever"
}
"""

NPM_MULTIPLE_VERSIONS = """\
{
    "name": "whatever",
    "version": "0.1.0",
    "version": "0.2.0",
}
"""

NPM2_PROVIDER = [
    (
        NPM_PACKAGE_JSON,
        NPM_PACKAGE_EXPECTED,
        None,
        None,
        None,
        None,
    ),
    (
        NPM_PACKAGE_JSON,
        NPM_PACKAGE_EXPECTED,
        NPM_LOCKFILE_JSON,
        NPM_LOCKFILE_EXPECTED,
        None,
        None,
    ),
    (
        NPM_PACKAGE_JSON,
        NPM_PACKAGE_EXPECTED,
        None,
        None,
        NPM_LOCKFILE_JSON,
        NPM_LOCKFILE_EXPECTED,
    ),
    (
        NPM_PACKAGE_JSON,
        NPM_PACKAGE_EXPECTED,
        NPM_LOCKFILE_JSON,
        NPM_LOCKFILE_EXPECTED,
        NPM_LOCKFILE_JSON,
        NPM_LOCKFILE_EXPECTED,
    ),
]


@pytest.mark.parametrize(
    "pkg_content,pkg_expected,pkg_lock_content,pkg_lock_expected,pkg_shrinkwrap_content,pkg_shrinkwrap_expected",
    NPM2_PROVIDER,
)
def test_npm2_provider(
    config: BaseConfig,
    chdir: Path,
    pkg_content: str,
    pkg_expected: str,
    pkg_lock_content: str,
    pkg_lock_expected: str,
    pkg_shrinkwrap_content: str,
    pkg_shrinkwrap_expected: str,
):
    pkg = chdir / "package.json"
    pkg.write_text(dedent(pkg_content))
    if pkg_lock_content:
        pkg_lock = chdir / "package-lock.json"
        pkg_lock.write_text(dedent(pkg_lock_content))
    if pkg_shrinkwrap_content:
        pkg_shrinkwrap = chdir / "npm-shrinkwrap.json"
        pkg_shrinkwrap.write_text(dedent(pkg_shrinkwrap_content))
    config.settings["version_provider"] = "npm2"

    provider = get_provider(config)
    assert isinstance(provider, Npm2Provider)
    assert provider.get_version() == "0.1.0"

    provider.set_version("42.1")
    assert pkg.read_text() == dedent(pkg_expected)
    if pkg_lock_content:
        assert pkg_lock.read_text() == dedent(pkg_lock_expected)
    if pkg_shrinkwrap_content:
        assert pkg_shrinkwrap.read_text() == dedent(pkg_shrinkwrap_expected)


def test_npm2_exceptions(
    config: BaseConfig,
):
    config.settings["version_provider"] = "npm2"
    provider = get_provider(config)
    assert isinstance(provider, Npm2Provider)
    with pytest.raises(ValueError):
        provider.get_package_version(NPM_NO_VERSION)
    with pytest.raises(ValueError):
        provider.get_package_version(NPM_MULTIPLE_VERSIONS)
