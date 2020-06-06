import pytest

from commitizen import defaults
from commitizen.config import BaseConfig


@pytest.fixture()
def config():
    _config = BaseConfig()
    _config.settings.update({"name": defaults.DEFAULT_SETTINGS["name"]})
    return _config
