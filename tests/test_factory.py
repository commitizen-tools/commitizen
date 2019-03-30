import pytest
from commitizen import factory, deafults, BaseCommitizen


def test_factory():
    config = {"name": deafults.NAME}
    r = factory.commiter_factory(config)
    assert isinstance(r, BaseCommitizen)


def test_factory_fails():
    config = {"name": "nothing"}
    with pytest.raises(SystemExit):
        factory.commiter_factory(config)
