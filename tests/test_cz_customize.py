import pytest
from tomlkit import parse

from commitizen.cz.customize import CustomizeCommitsCz
from commitizen.config import Config


@pytest.fixture(scope="module")
def config():
    _conf = Config()
    toml_str = """
    [tool.commitizen.customize]
    # message_template should follow the python string formatting spec
    message_template = "{change_type}: {message}"
    example = "feature: this feature eanable customize through config file"
    schema = "<type>: <body>"
    bump_pattern = "^(break|new|fix|hotfix)"
    bump_map = {"break" = "MAJOR", "new" = "MINOR", "fix" = "PATCH", "hotfix" = "PATCH"}
    info = "This is a customized cz."

    [[tool.commitizen.customize.questions]]
    type = "list"
    name = "change_type"
    choices = [
        {value = "feature", name = "feature: A new feature."},
        {value = "bug fix", name = "bug fix: A bug fix."}
    ]
    message = "Select the type of change you are committing"

    [[tool.commitizen.customize.questions]]
    type = "input"
    name = "message"
    message = "Body."
    """
    _conf.update(parse(toml_str)["tool"]["commitizen"])
    return _conf.config


def test_bump_pattern(config):
    cz = CustomizeCommitsCz(config)
    assert cz.bump_pattern == "^(break|new|fix|hotfix)"


def test_bump_map(config):
    cz = CustomizeCommitsCz(config)
    assert cz.bump_map == {
        "break": "MAJOR",
        "new": "MINOR",
        "fix": "PATCH",
        "hotfix": "PATCH",
    }


def test_questions(config):
    cz = CustomizeCommitsCz(config)
    questions = cz.questions()
    expected_questions = [
        {
            "type": "list",
            "name": "change_type",
            "choices": [
                {"value": "feature", "name": "feature: A new feature."},
                {"value": "bug fix", "name": "bug fix: A bug fix."},
            ],
            "message": "Select the type of change you are committing",
        },
        {"type": "input", "name": "message", "message": "Body."},
    ]
    assert list(questions) == expected_questions


def test_answer(config):
    cz = CustomizeCommitsCz(config)
    answers = {
        "change_type": "feature",
        "message": "this feature eanable customize through config file",
    }
    message = cz.message(answers)
    assert message == "feature: this feature eanable customize through config file"


def test_example(config):
    cz = CustomizeCommitsCz(config)
    assert "feature: this feature eanable customize through config file" in cz.example()


def test_schema(config):
    cz = CustomizeCommitsCz(config)
    assert "<type>: <body>" in cz.schema()


def test_info(config):
    cz = CustomizeCommitsCz(config)
    assert "This is a customized cz." in cz.info()
