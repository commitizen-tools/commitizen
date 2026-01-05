from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from commitizen.providers import get_provider
from commitizen.providers.uv_provider import UvProvider

if TYPE_CHECKING:
    from pytest_regressions.file_regression import FileRegressionFixture

    from commitizen.config.base_config import BaseConfig


PYPROJECT_TOML = """
[project]
name = "test-uv"
version = "4.2.1"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.13"
dependencies = ["commitizen==4.2.1"]
"""

PYPROJECT_TOML_UNDERSCORE = """
[project]
name = "test_uv"
version = "4.2.1"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.13"
dependencies = ["commitizen==4.2.1"]
"""

UV_LOCK_SIMPLIFIED = """
version = 1
revision = 1
requires-python = ">=3.13"

[[package]]
name = "commitizen"
version = "4.2.1"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "argcomplete" },
    { name = "charset-normalizer" },
    { name = "colorama" },
    { name = "decli" },
    { name = "jinja2" },
    { name = "packaging" },
    { name = "pyyaml" },
    { name = "questionary" },
    { name = "termcolor" },
    { name = "tomlkit" },
]
sdist = { url = "https://files.pythonhosted.org/packages/d8/a3/77ffc9aee014cbf46c84c9f156a1ddef2d4c7cfb87d567decf2541464245/commitizen-4.2.1.tar.gz", hash = "sha256:5255416f6d6071068159f0b97605777f3e25d00927ff157b7a8d01efeda7b952", size = 50645 }
wheels = [
    { url = "https://files.pythonhosted.org/packages/57/ce/2f5d8ebe8376991b5f805e9f33d20c7f4c9ca6155bdbda761117dc41dff1/commitizen-4.2.1-py3-none-any.whl", hash = "sha256:a347889e0fe408c3b920a34130d8f35616be3ea8ac6b7b20c5b9aac19762661b", size = 72646 },
]

[[package]]
name = "decli"
version = "0.6.2"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/3d/a0/a4658f93ecb589f479037b164dc13c68d108b50bf6594e54c820749f97ac/decli-0.6.2.tar.gz", hash = "sha256:36f71eb55fd0093895efb4f416ec32b7f6e00147dda448e3365cf73ceab42d6f", size = 7424 }
wheels = [
    { url = "https://files.pythonhosted.org/packages/bf/70/3ea48dc9e958d7d66c44c9944809181f1ca79aaef25703c023b5092d34ff/decli-0.6.2-py3-none-any.whl", hash = "sha256:2fc84106ce9a8f523ed501ca543bdb7e416c064917c12a59ebdc7f311a97b7ed", size = 7854 },
]

[[package]]
name = "test-uv"
version = "4.2.1"
source = { virtual = "." }
dependencies = [
    { name = "commitizen" },
]
"""


@pytest.mark.parametrize(
    "pyproject_content",
    [
        pytest.param(PYPROJECT_TOML, id="hyphenated"),
        pytest.param(PYPROJECT_TOML_UNDERSCORE, id="underscore"),
    ],
)
def test_uv_provider(
    config: BaseConfig,
    tmpdir,
    file_regression: FileRegressionFixture,
    pyproject_content: str,
):
    with tmpdir.as_cwd():
        pyproject_toml_file = tmpdir / UvProvider.filename
        pyproject_toml_file.write_text(pyproject_content, encoding="utf-8")

        uv_lock_file = tmpdir / UvProvider.lock_filename
        uv_lock_file.write_text(UV_LOCK_SIMPLIFIED, encoding="utf-8")

        config.settings["version_provider"] = "uv"

        provider = get_provider(config)
        assert isinstance(provider, UvProvider)
        assert provider.get_version() == "4.2.1"

        provider.set_version("100.100.100")
        assert provider.get_version() == "100.100.100"

        updated_pyproject_toml_content = pyproject_toml_file.read_text(encoding="utf-8")
        updated_uv_lock_content = uv_lock_file.read_text(encoding="utf-8")

        for content in (updated_pyproject_toml_content, updated_uv_lock_content):
            # updated project version
            assert "100.100.100" in content
            # commitizen version which was the same as project version and should not be affected
            assert "4.2.1" in content

        file_regression.check(updated_pyproject_toml_content, extension=".toml")
        file_regression.check(updated_uv_lock_content, extension=".lock")
