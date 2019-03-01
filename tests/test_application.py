import pytest
from commitizen.application import Application
from commitizen import BaseCommitizen, deafults


@pytest.fixture
def app():
    return Application(name=deafults.NAME)


def test_cz_is_returned(app):
    app = Application(name=deafults.NAME)
    assert isinstance(app.cz, BaseCommitizen)


def test_name_fails(app):
    app.name = None
    with pytest.raises(SystemExit):
        app.cz


def test_version(app):
    assert isinstance(app.version, str)


def test_list_version(app, capsys):
    app.detected_cz()
    out, err = capsys.readouterr()
    assert "cz_conventional_commits" in out
    assert isinstance(out, str)
