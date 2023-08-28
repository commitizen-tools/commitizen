from __future__ import annotations

import os
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Iterator

import pytest

from commitizen.config.base_config import BaseConfig
from commitizen.providers import get_provider
from commitizen.providers.cargo_provider import CargoProvider


if TYPE_CHECKING:
    pass


@pytest.fixture
def chdir(tmp_path: Path) -> Iterator[Path]:
    cwd = Path()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(cwd)


CARGO_TOML = """\
[package]
name = "whatever"
version = "0.1.0"
"""

CARGO_EXPECTED = """\
[package]
name = "whatever"
version = "42.1"
"""

CARGO_WORKSPACE_TOML = """\
[workspace.package]
name = "whatever"
version = "0.1.0"
"""

CARGO_WORKSPACE_EXPECTED = """\
[workspace.package]
name = "whatever"
version = "42.1"
"""


@pytest.mark.parametrize(
    "content, expected",
    (
        (CARGO_TOML, CARGO_EXPECTED),
        (CARGO_WORKSPACE_TOML, CARGO_WORKSPACE_EXPECTED),
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
