import pytest

from commitizen import defaults
from commitizen.config import BaseConfig
from commitizen.cz.jira import JiraSmartCz


@pytest.fixture()
def config():
    _config = BaseConfig()
    _config.settings.update({"name": defaults.DEFAULT_SETTINGS["name"]})
    return _config


def test_questions(config):
    cz = JiraSmartCz(config)
    questions = cz.questions()
    assert isinstance(questions, list)
    assert isinstance(questions[0], dict)


def test_answer(config):
    cz = JiraSmartCz(config)
    answers = {
        "message": "new test",
        "issues": "JRA-34",
        "workflow": "",
        "time": "",
        "comment": "",
    }
    message = cz.message(answers)
    assert message == "new test JRA-34"


def test_example(config):
    cz = JiraSmartCz(config)
    assert "JRA-34 #comment corrected indent issue\n" in cz.example()


def test_schema(config):
    cz = JiraSmartCz(config)
    assert "<ignored text>" in cz.schema()


def test_info(config):
    cz = JiraSmartCz(config)
    assert (
        "Smart Commits allow repository committers to perform "
        "actions such as transitioning JIRA Software"
    ) in cz.info()
