import os

import pytest

from commitizen import defaults
from commitizen.config import BaseConfig


@pytest.fixture()
def config():
    _config = BaseConfig()
    _config.settings.update({"name": defaults.name})
    return _config


@pytest.fixture()  # type: ignore
def changelog_path() -> str:
    return os.path.join(os.getcwd(), "CHANGELOG.md")


@pytest.fixture()  # type: ignore
def config_path() -> str:
    return os.path.join(os.getcwd(), "pyproject.toml")
