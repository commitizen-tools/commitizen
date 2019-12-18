import pytest

from commitizen import BaseCommitizen, defaults, factory
from commitizen.config import BaseConfig


def test_factory():
    config = BaseConfig()
    config._settings["name"] = defaults.name
    r = factory.commiter_factory(config)
    assert isinstance(r, BaseCommitizen)


def test_factory_fails():
    config = BaseConfig()
    config._settings["name"] = "Nothing"
    with pytest.raises(SystemExit):
        factory.commiter_factory(config)
