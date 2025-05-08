from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from commitizen.config.base_config import BaseConfig
from commitizen.providers import get_provider
from commitizen.providers.cargo_provider import CargoProvider

CARGO_TOML = """\
[package]
name = "whatever"
version = "0.1.0"
"""

CARGO_TOML_EXPECTED = """\
[package]
name = "whatever"
version = "42.1"
"""

CARGO_WORKSPACE_TOML = """\
[workspace.package]
name = "whatever"
version = "0.1.0"
"""

CARGO_WORKSPACE_TOML_EXPECTED = """\
[workspace.package]
name = "whatever"
version = "42.1"
"""

CARGO_LOCK = """\
[[package]]
name = "whatever"
version = "0.1.0"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "123abc"
dependencies = [
 "packageA",
 "packageB",
 "packageC",
]
"""

CARGO_LOCK_EXPECTED = """\
[[package]]
name = "whatever"
version = "42.1"
source = "registry+https://github.com/rust-lang/crates.io-index"
checksum = "123abc"
dependencies = [
 "packageA",
 "packageB",
 "packageC",
]
"""


@pytest.mark.parametrize(
    "content, expected",
    (
        (CARGO_TOML, CARGO_TOML_EXPECTED),
        (CARGO_WORKSPACE_TOML, CARGO_WORKSPACE_TOML_EXPECTED),
    ),
)
def test_cargo_provider(
    config: BaseConfig,
    chdir: Path,
    content: str,
    expected: str,
):
    filename = CargoProvider.filename
    file = chdir / filename
    file.write_text(dedent(content))
    config.settings["version_provider"] = "cargo"

    provider = get_provider(config)
    assert isinstance(provider, CargoProvider)
    assert provider.get_version() == "0.1.0"

    provider.set_version("42.1")
    assert file.read_text() == dedent(expected)


@pytest.mark.parametrize(
    "toml_content, lock_content, toml_expected, lock_expected",
    (
        (
            CARGO_TOML,
            CARGO_LOCK,
            CARGO_TOML_EXPECTED,
            CARGO_LOCK_EXPECTED,
        ),
        (
            CARGO_WORKSPACE_TOML,
            CARGO_LOCK,
            CARGO_WORKSPACE_TOML_EXPECTED,
            CARGO_LOCK_EXPECTED,
        ),
    ),
)
def test_cargo_provider_with_lock(
    config: BaseConfig,
    chdir: Path,
    toml_content: str,
    lock_content: str,
    toml_expected: str,
    lock_expected: str,
):
    filename = CargoProvider.filename
    file = chdir / filename
    file.write_text(dedent(toml_content))

    lock_filename = CargoProvider.lock_filename
    lock_file = chdir / lock_filename
    lock_file.write_text(dedent(lock_content))
    config.settings["version_provider"] = "cargo"

    provider = get_provider(config)
    assert isinstance(provider, CargoProvider)
    assert provider.get_version() == "0.1.0"

    provider.set_version("42.1")
    assert file.read_text() == dedent(toml_expected)
    assert lock_file.read_text() == dedent(lock_expected)
