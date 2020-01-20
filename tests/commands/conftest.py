import pytest

from commitizen import defaults
from commitizen.config import BaseConfig


@pytest.fixture()
def config():
    _config = BaseConfig()
    _config.settings.update({"name": defaults.name})
    return _config
