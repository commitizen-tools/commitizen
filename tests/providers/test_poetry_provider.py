from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from commitizen.config.base_config import BaseConfig
from commitizen.providers import get_provider
from commitizen.providers.poetry_provider import PoetryProvider

POETRY_TOML = """\
[tool.poetry]
version = "0.1.0"
"""

POETRY_EXPECTED = """\
[tool.poetry]
version = "42.1"
"""


@pytest.mark.parametrize(
    "content, expected",
    ((POETRY_TOML, POETRY_EXPECTED),),
)
def test_cargo_provider(
    config: BaseConfig,
    chdir: Path,
    content: str,
    expected: str,
):
    filename = PoetryProvider.filename
    file = chdir / filename
    file.write_text(dedent(content))
    config.settings["version_provider"] = "poetry"

    provider = get_provider(config)
    assert isinstance(provider, PoetryProvider)
    assert provider.get_version() == "0.1.0"

    provider.set_version("42.1")
    assert file.read_text() == dedent(expected)
