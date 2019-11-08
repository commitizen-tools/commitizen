import pytest

from commitizen import BaseCommitizen, defaults, factory


def test_factory():
    config = {"name": defaults.name}
    r = factory.commiter_factory(config)
    assert isinstance(r, BaseCommitizen)


def test_factory_fails():
    config = {"name": "nothing"}
    with pytest.raises(SystemExit):
        factory.commiter_factory(config)
