from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from commitizen.providers import get_provider
from commitizen.providers.pep751_provider import Pep751Provider

if TYPE_CHECKING:
    from pathlib import Path

    from commitizen.config.base_config import BaseConfig

PYPROJECT_TOML = """\
[project]
name = "my-package"
version = "0.1.0"
"""

PYPROJECT_TOML_EXPECTED = """\
[project]
name = "my-package"
version = "42.1"
"""

PYLOCK_TOML_WITH_DIRECTORY = """\
lock-version = "1.0"
created-by = "test"

[[packages]]
name = "my-package"
version = "0.1.0"

[packages.directory]
path = "."
editable = true

[[packages]]
name = "some-dep"
version = "1.2.3"
"""

PYLOCK_TOML_WITH_DIRECTORY_EXPECTED = """\
lock-version = "1.0"
created-by = "test"

[[packages]]
name = "my-package"
version = "42.1"

[packages.directory]
path = "."
editable = true

[[packages]]
name = "some-dep"
version = "1.2.3"
"""

PYLOCK_TOML_NON_MATCHING_NAME = """\
lock-version = "1.0"
created-by = "test"

[[packages]]
name = "other-package"
version = "0.1.0"

[packages.directory]
path = "."
editable = true
"""

PYLOCK_TOML_NON_DIRECTORY = """\
lock-version = "1.0"
created-by = "test"

[[packages]]
name = "my-package"
version = "0.1.0"
"""


@pytest.fixture
def pyproject(chdir: Path) -> Path:
    file = chdir / "pyproject.toml"
    file.write_text(dedent(PYPROJECT_TOML))
    return file


def test_get_version(config: BaseConfig, pyproject: Path):
    config.settings["version_provider"] = "pep751"
    provider = get_provider(config)
    assert isinstance(provider, Pep751Provider)
    assert provider.get_version() == "0.1.0"


def test_set_version_without_lock_files(
    config: BaseConfig, pyproject: Path, chdir: Path
):
    config.settings["version_provider"] = "pep751"
    provider = get_provider(config)

    provider.set_version("42.1")

    assert pyproject.read_text() == dedent(PYPROJECT_TOML_EXPECTED)
    # No pylock*.toml files should exist
    assert list(chdir.glob("pylock*.toml")) == []


def test_set_version_with_pylock_toml(config: BaseConfig, pyproject: Path, chdir: Path):
    lock_file = chdir / "pylock.toml"
    lock_file.write_text(dedent(PYLOCK_TOML_WITH_DIRECTORY))
    config.settings["version_provider"] = "pep751"
    provider = get_provider(config)

    provider.set_version("42.1")

    assert pyproject.read_text() == dedent(PYPROJECT_TOML_EXPECTED)
    assert lock_file.read_text() == dedent(PYLOCK_TOML_WITH_DIRECTORY_EXPECTED)


def test_set_version_with_named_lock_file(
    config: BaseConfig, pyproject: Path, chdir: Path
):
    lock_file = chdir / "pylock.dev.toml"
    lock_file.write_text(dedent(PYLOCK_TOML_WITH_DIRECTORY))
    config.settings["version_provider"] = "pep751"
    provider = get_provider(config)

    provider.set_version("42.1")

    assert pyproject.read_text() == dedent(PYPROJECT_TOML_EXPECTED)
    assert lock_file.read_text() == dedent(PYLOCK_TOML_WITH_DIRECTORY_EXPECTED)


def test_set_version_non_matching_package_not_updated(
    config: BaseConfig, pyproject: Path, chdir: Path
):
    lock_file = chdir / "pylock.toml"
    lock_file.write_text(dedent(PYLOCK_TOML_NON_MATCHING_NAME))
    original_lock_content = lock_file.read_text()
    config.settings["version_provider"] = "pep751"
    provider = get_provider(config)

    provider.set_version("42.1")

    assert pyproject.read_text() == dedent(PYPROJECT_TOML_EXPECTED)
    # Lock file should be unchanged since no matching package name
    assert lock_file.read_text() == original_lock_content


def test_set_version_non_directory_source_not_updated(
    config: BaseConfig, pyproject: Path, chdir: Path
):
    lock_file = chdir / "pylock.toml"
    lock_file.write_text(dedent(PYLOCK_TOML_NON_DIRECTORY))
    original_lock_content = lock_file.read_text()
    config.settings["version_provider"] = "pep751"
    provider = get_provider(config)

    provider.set_version("42.1")

    assert pyproject.read_text() == dedent(PYPROJECT_TOML_EXPECTED)
    # Lock file should be unchanged since package has no directory source
    assert lock_file.read_text() == original_lock_content


def test_set_version_multiple_lock_files(
    config: BaseConfig, pyproject: Path, chdir: Path
):
    lock_file1 = chdir / "pylock.toml"
    lock_file1.write_text(dedent(PYLOCK_TOML_WITH_DIRECTORY))
    lock_file2 = chdir / "pylock.dev.toml"
    lock_file2.write_text(dedent(PYLOCK_TOML_WITH_DIRECTORY))
    config.settings["version_provider"] = "pep751"
    provider = get_provider(config)

    provider.set_version("42.1")

    assert pyproject.read_text() == dedent(PYPROJECT_TOML_EXPECTED)
    assert lock_file1.read_text() == dedent(PYLOCK_TOML_WITH_DIRECTORY_EXPECTED)
    assert lock_file2.read_text() == dedent(PYLOCK_TOML_WITH_DIRECTORY_EXPECTED)


def test_provider_registration(config: BaseConfig, pyproject: Path):
    config.settings["version_provider"] = "pep751"
    provider = get_provider(config)
    assert isinstance(provider, Pep751Provider)
