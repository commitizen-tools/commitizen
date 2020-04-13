import pytest

from commitizen.config import BaseConfig, TomlConfig
from commitizen.cz.customize import CustomizeCommitsCz
from commitizen.error_codes import MISSING_CONFIG


@pytest.fixture(scope="module")
def config():
    toml_str = r"""
    [tool.commitizen.customize]
    message_template = "{{change_type}}:{% if show_message %} {{message}}{% endif %}"
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

    [[tool.commitizen.customize.questions]]
    type = "confirm"
    name = "show_message"
    message = "Do you want to add body message in commit?"
    """
    return TomlConfig(data=toml_str, path="not_exist.toml")


def test_initialize_cz_customize_failed():
    with pytest.raises(SystemExit) as excinfo:
        config = BaseConfig()
        _ = CustomizeCommitsCz(config)

    assert excinfo.value.code == MISSING_CONFIG


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
        {
            "type": "confirm",
            "name": "show_message",
            "message": "Do you want to add body message in commit?",
        },
    ]
    assert list(questions) == expected_questions


def test_answer(config):
    cz = CustomizeCommitsCz(config)
    answers = {
        "change_type": "feature",
        "message": "this feature eanable customize through config file",
        "show_message": True,
    }
    message = cz.message(answers)
    assert message == "feature: this feature eanable customize through config file"

    cz = CustomizeCommitsCz(config)
    answers = {
        "change_type": "feature",
        "message": "this feature eanable customize through config file",
        "show_message": False,
    }
    message = cz.message(answers)
    assert message == "feature:"


def test_example(config):
    cz = CustomizeCommitsCz(config)
    assert "feature: this feature eanable customize through config file" in cz.example()


def test_schema(config):
    cz = CustomizeCommitsCz(config)
    assert "<type>: <body>" in cz.schema()


def test_info(config):
    cz = CustomizeCommitsCz(config)
    assert "This is a customized cz." in cz.info()
