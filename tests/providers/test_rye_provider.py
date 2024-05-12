from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from commitizen.config.base_config import BaseConfig
from commitizen.providers import get_provider
from commitizen.providers.base_provider import VersionProvider
from commitizen.providers.rye_provider import RyeProvider


RYE_TOML = """\
[tool.rye]
version = "0.1.0"
"""

RYE_EXPECTED = """\
[tool.rye]
version = "42.1"
"""


@pytest.mark.parametrize(
    "content, expected",
    ((RYE_TOML, RYE_EXPECTED),),
)
def test_rye_provider(
    config: BaseConfig,
    chdir: Path,
    content: str,
    expected: str,
):
    filename = RyeProvider.filename
    file = chdir / filename
    file.write_text(dedent(content))
    config.settings["version_provider"] = "rye"

    provider: VersionProvider = get_provider(config)
    assert isinstance(provider, RyeProvider)
    assert provider.get_version() == "0.1.0"

    provider.set_version("42.1")
    assert file.read_text() == dedent(expected)
