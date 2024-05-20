from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from commitizen.config.base_config import BaseConfig
from commitizen.providers import get_provider
from commitizen.providers.pep621_provider import Pep621Provider

PEP621_TOML = """\
[project]
version = "0.1.0"
"""

PEP621_EXPECTED = """\
[project]
version = "42.1"
"""


@pytest.mark.parametrize(
    "content, expected",
    ((PEP621_TOML, PEP621_EXPECTED),),
)
def test_cargo_provider(
    config: BaseConfig,
    chdir: Path,
    content: str,
    expected: str,
):
    filename = Pep621Provider.filename
    file = chdir / filename
    file.write_text(dedent(content))
    config.settings["version_provider"] = "pep621"

    provider = get_provider(config)
    assert isinstance(provider, Pep621Provider)
    assert provider.get_version() == "0.1.0"

    provider.set_version("42.1")
    assert file.read_text() == dedent(expected)
