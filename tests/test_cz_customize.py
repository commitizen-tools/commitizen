import pytest
from pytest_mock import MockFixture

from commitizen import cmd, commands
from commitizen.config import BaseConfig, JsonConfig, TomlConfig, YAMLConfig
from commitizen.cz.customize import CustomizeCommitsCz
from commitizen.cz.utils import (
    multiple_line_breaker,
    required_validator,
    required_validator_scope,
    required_validator_subject_strip,
    required_validator_title_strip,
)
from commitizen.exceptions import MissingCzCustomizeConfigError, NotAllowed

TOML_STR = r"""
    [tool.commitizen]
    name = "cz_customize"
    version = "1.0.0"
    version_files = [
        "commitizen/__version__.py",
        "pyproject.toml"
    ]

    [tool.commitizen.customize]
    message_template = "{{change_type}}:{% if show_message %} {{message}}{% endif %}"
    example = "feature: this feature enables customization through a config file"
    schema = "<type>: <body>"
    schema_pattern = "(feature|bug fix):(\\s.*)"
    commit_parser = "^(?P<change_type>feature|bug fix):\\s(?P<message>.*)?"
    changelog_pattern = "^(feature|bug fix)?(!)?"
    change_type_map = {"feature" = "Feat", "bug fix" = "Fix"}

    bump_pattern = "^(break|new|fix|hotfix)"
    bump_map = {"break" = "MAJOR", "new" = "MINOR", "fix" = "PATCH", "hotfix" = "PATCH"}
    change_type_order = ["perf", "BREAKING CHANGE", "feat", "fix", "refactor"]
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
    name = "subject"
    message = "Subject."
    filter = "required_validator_subject_strip"

    [[tool.commitizen.customize.questions]]
    type = "input"
    name = "message"
    message = "Body."
    filter = "multiple_line_breaker"

    [[tool.commitizen.customize.questions]]
    type = "confirm"
    name = "show_message"
    message = "Do you want to add body message in commit?"
"""

JSON_STR = r"""
    {
        "commitizen": {
            "name": "cz_customize",
            "version": "1.0.0",
            "version_files": [
                "commitizen/__version__.py",
                "pyproject.toml"
            ],
            "customize": {
                "message_template": "{{change_type}}:{% if show_message %} {{message}}{% endif %}",
                "example": "feature: this feature enables customization through a config file",
                "schema": "<type>: <body>",
                "schema_pattern": "(feature|bug fix):(\\s.*)",
                "bump_pattern": "^(break|new|fix|hotfix)",
                "bump_map": {
                    "break": "MAJOR",
                    "new": "MINOR",
                    "fix": "PATCH",
                    "hotfix": "PATCH"
                },
                "commit_parser": "^(?P<change_type>feature|bug fix):\\s(?P<message>.*)?",
                "changelog_pattern": "^(feature|bug fix)?(!)?",
                "change_type_map": {"feature": "Feat", "bug fix": "Fix"},
                "change_type_order": ["perf", "BREAKING CHANGE", "feat", "fix", "refactor"],
                "info": "This is a customized cz.",
                "questions": [
                    {
                        "type": "list",
                        "name": "change_type",
                        "choices": [
                            {
                                "value": "feature",
                                "name": "feature: A new feature."
                            },
                            {
                                "value": "bug fix",
                                "name": "bug fix: A bug fix."
                            }
                        ],
                        "message": "Select the type of change you are committing"
                    },
                    {
                        "type": "input",
                        "name": "subject",
                        "message": "Subject.",
                        "filter": "required_validator_subject_strip"
                    },
                    {
                        "type": "input",
                        "name": "message",
                        "message": "Body.",
                        "filter": "multiple_line_breaker"
                    },
                    {
                        "type": "confirm",
                        "name": "show_message",
                        "message": "Do you want to add body message in commit?"
                    }
                ]
            }
        }
    }
"""

YAML_STR = """
commitizen:
  name: cz_customize
  version: 1.0.0
  version_files:
  - commitizen/__version__.py
  - pyproject.toml
  customize:
    message_template: '{{change_type}}:{% if show_message %} {{message}}{% endif %}'
    example: 'feature: this feature enables customization through a config file'
    schema: '<type>: <body>'
    schema_pattern: '(feature|bug fix):(\\s.*)'
    bump_pattern: '^(break|new|fix|hotfix)'
    commit_parser: '^(?P<change_type>feature|bug fix):\\s(?P<message>.*)?'
    changelog_pattern: '^(feature|bug fix)?(!)?'
    change_type_map:
      feature: Feat
      bug fix: Fix
    bump_map:
      break: MAJOR
      new: MINOR
      fix: PATCH
      hotfix: PATCH
    change_type_order: ['perf', 'BREAKING CHANGE', 'feat', 'fix', 'refactor']
    info: This is a customized cz.
    questions:
    - type: list
      name: change_type
      choices:
      - value: feature
        name: 'feature: A new feature.'
      - value: bug fix
        name: 'bug fix: A bug fix.'
      message: Select the type of change you are committing
    - type: input
      name: subject
      message: Subject.
      filter: required_validator_subject_strip
    - type: input
      name: message
      message: Body.
      filter: multiple_line_breaker
    - type: confirm
      name: show_message
      message: Do you want to add body message in commit?
"""

TOML_WITH_UNICODE = r"""
    [tool.commitizen]
    name = "cz_customize"
    version = "1.0.0"
    version_files = [
        "commitizen/__version__.py",
        "pyproject.toml:version"
    ]
    [tool.commitizen.customize]
    message_template = "{{change_type}}:{% if show_message %} {{message}}{% endif %}"
    example = "✨ feature: this feature enables customization through a config file"
    schema = "<type>: <body>"
    schema_pattern = "(✨ feature|🐛 bug fix):(\\s.*)"
    commit_parser = "^(?P<change_type>✨ feature|🐛 bug fix):\\s(?P<message>.*)?"
    changelog_pattern = "^(✨ feature|🐛 bug fix)?(!)?"
    change_type_map = {"✨ feature" = "Feat", "🐛 bug fix" = "Fix"}
    bump_pattern = "^(✨ feat|🐛 bug fix)"
    bump_map = {"break" = "MAJOR", "✨ feat" = "MINOR", "🐛 bug fix" = "MINOR"}
    change_type_order = ["perf", "BREAKING CHANGE", "feat", "fix", "refactor"]
    info = "This is a customized cz with emojis 🎉!"
    [[tool.commitizen.customize.questions]]
    type = "list"
    name = "change_type"
    choices = [
        {value = "✨ feature", name = "✨ feature: A new feature."},
        {value = "🐛 bug fix", name = "🐛 bug fix: A bug fix."}
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

JSON_WITH_UNICODE = r"""
    {
        "commitizen": {
            "name": "cz_customize",
            "version": "1.0.0",
            "version_files": [
                "commitizen/__version__.py",
                "pyproject.toml:version"
            ],
            "customize": {
                "message_template": "{{change_type}}:{% if show_message %} {{message}}{% endif %}",
                "example": "✨ feature: this feature enables customization through a config file",
                "schema": "<type>: <body>",
                "schema_pattern": "(✨ feature|🐛 bug fix):(\\s.*)",
                "bump_pattern": "^(✨ feat|🐛 bug fix)",
                "bump_map": {
                    "break": "MAJOR",
                    "✨ feat": "MINOR",
                    "🐛 bug fix": "MINOR"
                },
                "commit_parser": "^(?P<change_type>✨ feature|🐛 bug fix):\\s(?P<message>.*)?",
                "changelog_pattern": "^(✨ feature|🐛 bug fix)?(!)?",
                "change_type_map": {"✨ feature": "Feat", "🐛 bug fix": "Fix"},
                "change_type_order": ["perf", "BREAKING CHANGE", "feat", "fix", "refactor"],
                "info": "This is a customized cz with emojis 🎉!",
                "questions": [
                    {
                        "type": "list",
                        "name": "change_type",
                        "choices": [
                            {
                                "value": "✨ feature",
                                "name": "✨ feature: A new feature."
                            },
                            {
                                "value": "🐛 bug fix",
                                "name": "🐛 bug fix: A bug fix."
                            }
                        ],
                        "message": "Select the type of change you are committing"
                    },
                    {
                        "type": "input",
                        "name": "message",
                        "message": "Body."
                    },
                    {
                        "type": "confirm",
                        "name": "show_message",
                        "message": "Do you want to add body message in commit?"
                    }
                ]
            }
        }
    }
"""

TOML_STR_INFO_PATH = """
    [tool.commitizen.customize]
    message_template = "{{change_type}}:{% if show_message %} {{message}}{% endif %}"
    example = "feature: this feature enables customization through a config file"
    schema = "<type>: <body>"
    bump_pattern = "^(break|new|fix|hotfix)"
    bump_map = {"break" = "MAJOR", "new" = "MINOR", "fix" = "PATCH", "hotfix" = "PATCH"}
    info_path = "info.txt"
"""

JSON_STR_INFO_PATH = r"""
    {
        "commitizen": {
            "customize": {
                "message_template": "{{change_type}}:{% if show_message %} {{message}}{% endif %}",
                "example": "feature: this feature enables customization through a config file",
                "schema": "<type>: <body>",
                "bump_pattern": "^(break|new|fix|hotfix)",
                "bump_map": {
                    "break": "MAJOR",
                    "new": "MINOR",
                    "fix": "PATCH",
                    "hotfix": "PATCH"
                },
                "info_path": "info.txt"
            }
        }
    }
"""

YAML_STR_INFO_PATH = """
commitizen:
  customize:
    message_template: "{{change_type}}:{% if show_message %} {{message}}{% endif %}"
    example: 'feature: this feature enables customization through a config file'
    schema: "<type>: <body>"
    bump_pattern: "^(break|new|fix|hotfix)"
    bump_map:
      break: MAJOR
      new: MINOR
      fix: PATCH
      hotfix: PATCH
    info_path: info.txt
"""

TOML_STR_WITHOUT_INFO = """
    [tool.commitizen.customize]
    message_template = "{{change_type}}:{% if show_message %} {{message}}{% endif %}"
    example = "feature: this feature enables customization through a config file"
    schema = "<type>: <body>"
    bump_pattern = "^(break|new|fix|hotfix)"
    bump_map = {"break" = "MAJOR", "new" = "MINOR", "fix" = "PATCH", "hotfix" = "PATCH"}
"""

JSON_STR_WITHOUT_PATH = r"""
    {
        "commitizen": {
            "customize": {
                "message_template": "{{change_type}}:{% if show_message %} {{message}}{% endif %}",
                "example": "feature: this feature enables customization through a config file",
                "schema": "<type>: <body>",
                "bump_pattern": "^(break|new|fix|hotfix)",
                "bump_map": {
                    "break": "MAJOR",
                    "new": "MINOR",
                    "fix": "PATCH",
                    "hotfix": "PATCH"
                }
            }
        }
    }
"""

YAML_STR_WITHOUT_PATH = """
commitizen:
  customize:
    message_template: "{{change_type}}:{% if show_message %} {{message}}{% endif %}"
    example: 'feature: this feature enables customization through a config file'
    schema: "<type>: <body>"
    bump_pattern: "^(break|new|fix|hotfix)"
    bump_map:
      break: MAJOR
      new: MINOR
      fix: PATCH
      hotfix: PATCH
"""


@pytest.fixture
def staging_is_clean(mocker: MockFixture, tmp_git_project):
    is_staging_clean_mock = mocker.patch("commitizen.git.is_staging_clean")
    is_staging_clean_mock.return_value = False
    return tmp_git_project


@pytest.fixture(
    params=[
        TomlConfig(data=TOML_STR, path="not_exist.toml"),
        JsonConfig(data=JSON_STR, path="not_exist.json"),
        YAMLConfig(data=YAML_STR, path="not_exist.yaml"),
    ]
)
def config(request):
    """Parametrize the config fixture

    This fixture allow to test multiple config formats,
    without add the builtin parametrize decorator
    """
    return request.param


@pytest.fixture(
    params=[
        YAMLConfig(data=YAML_STR, path="not_exist.yaml"),
    ]
)
def config_filters(request):
    return request.param


@pytest.fixture(
    params=[
        TomlConfig(data=TOML_STR_INFO_PATH, path="not_exist.toml"),
        JsonConfig(data=JSON_STR_INFO_PATH, path="not_exist.json"),
        YAMLConfig(data=YAML_STR_INFO_PATH, path="not_exist.yaml"),
    ]
)
def config_info(request):
    return request.param


@pytest.fixture(
    params=[
        TomlConfig(data=TOML_STR_WITHOUT_INFO, path="not_exist.toml"),
        JsonConfig(data=JSON_STR_WITHOUT_PATH, path="not_exist.json"),
        YAMLConfig(data=YAML_STR_WITHOUT_PATH, path="not_exist.yaml"),
    ]
)
def config_without_info(request):
    return request.param


@pytest.fixture(
    params=[
        TomlConfig(data=TOML_WITH_UNICODE, path="not_exist.toml"),
        JsonConfig(data=JSON_WITH_UNICODE, path="not_exist.json"),
    ]
)
def config_with_unicode(request):
    return request.param


def test_initialize_cz_customize_failed():
    with pytest.raises(MissingCzCustomizeConfigError) as excinfo:
        config = BaseConfig()
        _ = CustomizeCommitsCz(config)

    assert MissingCzCustomizeConfigError.message in str(excinfo.value)


def test_bump_pattern(config):
    cz = CustomizeCommitsCz(config)
    assert cz.bump_pattern == "^(break|new|fix|hotfix)"


def test_bump_pattern_unicode(config_with_unicode):
    cz = CustomizeCommitsCz(config_with_unicode)
    assert cz.bump_pattern == "^(✨ feat|🐛 bug fix)"


def test_bump_map(config):
    cz = CustomizeCommitsCz(config)
    assert cz.bump_map == {
        "break": "MAJOR",
        "new": "MINOR",
        "fix": "PATCH",
        "hotfix": "PATCH",
    }


def test_bump_map_unicode(config_with_unicode):
    cz = CustomizeCommitsCz(config_with_unicode)
    assert cz.bump_map == {
        "break": "MAJOR",
        "✨ feat": "MINOR",
        "🐛 bug fix": "MINOR",
    }


def test_change_type_order(config):
    cz = CustomizeCommitsCz(config)
    assert cz.change_type_order == [
        "perf",
        "BREAKING CHANGE",
        "feat",
        "fix",
        "refactor",
    ]


def test_change_type_order_unicode(config_with_unicode):
    cz = CustomizeCommitsCz(config_with_unicode)
    assert cz.change_type_order == [
        "perf",
        "BREAKING CHANGE",
        "feat",
        "fix",
        "refactor",
    ]


def test_questions_default(config):
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
        {
            "type": "input",
            "name": "subject",
            "message": "Subject.",
            "filter": "required_validator_subject_strip",
        },
        {
            "type": "input",
            "name": "message",
            "message": "Body.",
            "filter": "multiple_line_breaker",
        },
        {
            "type": "confirm",
            "name": "show_message",
            "message": "Do you want to add body message in commit?",
        },
    ]
    assert list(questions) == expected_questions


@pytest.mark.usefixtures("staging_is_clean")
def test_questions_filter_default(config, mocker: MockFixture):
    is_staging_clean_mock = mocker.patch("commitizen.git.is_staging_clean")
    is_staging_clean_mock.return_value = False

    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "change_type": "feature",
        "subject": "user created",
        "message": "body of the commit",
        "show_message": True,
    }

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", b"", b"", 0)

    commands.Commit(config, {})()

    prompts_questions = prompt_mock.call_args[0][0]
    assert prompts_questions[0]["type"] == "list"
    assert prompts_questions[0]["name"] == "change_type"
    assert prompts_questions[0]["use_shortcuts"] is False
    assert prompts_questions[1]["type"] == "input"
    assert prompts_questions[1]["name"] == "subject"
    assert prompts_questions[1]["filter"] == required_validator_subject_strip
    assert prompts_questions[2]["type"] == "input"
    assert prompts_questions[2]["name"] == "message"
    assert prompts_questions[2]["filter"] == multiple_line_breaker
    assert prompts_questions[3]["type"] == "confirm"
    assert prompts_questions[3]["name"] == "show_message"


@pytest.mark.usefixtures("staging_is_clean")
def test_questions_filter_values(config_filters, mocker: MockFixture):
    is_staging_clean_mock = mocker.patch("commitizen.git.is_staging_clean")
    is_staging_clean_mock.return_value = False

    prompt_mock = mocker.patch("questionary.prompt")
    prompt_mock.return_value = {
        "change_type": "feature",
        "subject": "user created",
        "message": "body of the commit",
        "show_message": True,
    }

    commit_mock = mocker.patch("commitizen.git.commit")
    commit_mock.return_value = cmd.Command("success", "", b"", b"", 0)

    commit_cmd = commands.Commit(config_filters, {})

    assert isinstance(commit_cmd.cz, CustomizeCommitsCz)

    for filter_desc in [
        ("multiple_line_breaker", multiple_line_breaker),
        ("required_validator", required_validator),
        ("required_validator_scope", required_validator_scope),
        ("required_validator_subject_strip", required_validator_subject_strip),
        ("required_validator_title_strip", required_validator_title_strip),
    ]:
        commit_cmd.cz.custom_settings["questions"][1]["filter"] = filter_desc[0]  # type: ignore[index]
        commit_cmd()

        assert filter_desc[1]("input")

        prompts_questions = prompt_mock.call_args[0][0]
        assert prompts_questions[1]["filter"] == filter_desc[1]

    for filter_name in [
        "",
        "faulty_value",
    ]:
        commit_cmd.cz.custom_settings["questions"][1]["filter"] = filter_name  # type: ignore[index]

        with pytest.raises(NotAllowed):
            commit_cmd()


def test_questions_unicode(config_with_unicode):
    cz = CustomizeCommitsCz(config_with_unicode)
    questions = cz.questions()
    expected_questions = [
        {
            "type": "list",
            "name": "change_type",
            "choices": [
                {"value": "✨ feature", "name": "✨ feature: A new feature."},
                {"value": "🐛 bug fix", "name": "🐛 bug fix: A bug fix."},
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
        "message": "this feature enaable customize through config file",
        "show_message": True,
    }
    message = cz.message(answers)
    assert message == "feature: this feature enaable customize through config file"

    cz = CustomizeCommitsCz(config)
    answers = {
        "change_type": "feature",
        "message": "this feature enaable customize through config file",
        "show_message": False,
    }
    message = cz.message(answers)
    assert message == "feature:"


def test_answer_unicode(config_with_unicode):
    cz = CustomizeCommitsCz(config_with_unicode)
    answers = {
        "change_type": "✨ feature",
        "message": "this feature enables customization through a config file",
        "show_message": True,
    }
    message = cz.message(answers)
    assert (
        message
        == "✨ feature: this feature enables customization through a config file"
    )

    cz = CustomizeCommitsCz(config_with_unicode)
    answers = {
        "change_type": "✨ feature",
        "message": "this feature enables customization through a config file",
        "show_message": False,
    }
    message = cz.message(answers)
    assert message == "✨ feature:"


def test_example(config):
    cz = CustomizeCommitsCz(config)
    assert (
        "feature: this feature enables customization through a config file"
        in cz.example()
    )


def test_example_unicode(config_with_unicode):
    cz = CustomizeCommitsCz(config_with_unicode)
    assert (
        "✨ feature: this feature enables customization through a config file"
        in cz.example()
    )


def test_schema(config):
    cz = CustomizeCommitsCz(config)
    assert "<type>: <body>" in cz.schema()


def test_schema_pattern(config):
    cz = CustomizeCommitsCz(config)
    assert r"(feature|bug fix):(\s.*)" in cz.schema_pattern()


def test_schema_pattern_unicode(config_with_unicode):
    cz = CustomizeCommitsCz(config_with_unicode)
    assert r"(✨ feature|🐛 bug fix):(\s.*)" in cz.schema_pattern()


def test_info(config):
    cz = CustomizeCommitsCz(config)
    assert "This is a customized cz." in cz.info()


def test_info_unicode(config_with_unicode):
    cz = CustomizeCommitsCz(config_with_unicode)
    assert "This is a customized cz with emojis 🎉!" in cz.info()


def test_info_with_info_path(tmpdir, config_info):
    with tmpdir.as_cwd():
        tmpfile = tmpdir.join("info.txt")
        tmpfile.write("Test info")

        cz = CustomizeCommitsCz(config_info)
        assert "Test info" in cz.info()


def test_info_without_info(config_without_info):
    cz = CustomizeCommitsCz(config_without_info)
    assert cz.info() == ""


def test_commit_parser(config):
    cz = CustomizeCommitsCz(config)
    assert cz.commit_parser == "^(?P<change_type>feature|bug fix):\\s(?P<message>.*)?"


def test_commit_parser_unicode(config_with_unicode):
    cz = CustomizeCommitsCz(config_with_unicode)
    assert (
        cz.commit_parser
        == "^(?P<change_type>✨ feature|🐛 bug fix):\\s(?P<message>.*)?"
    )


def test_changelog_pattern(config):
    cz = CustomizeCommitsCz(config)
    assert cz.changelog_pattern == "^(feature|bug fix)?(!)?"


def test_changelog_pattern_unicode(config_with_unicode):
    cz = CustomizeCommitsCz(config_with_unicode)
    assert cz.changelog_pattern == "^(✨ feature|🐛 bug fix)?(!)?"


def test_change_type_map(config):
    cz = CustomizeCommitsCz(config)
    assert cz.change_type_map == {"feature": "Feat", "bug fix": "Fix"}


def test_change_type_map_unicode(config_with_unicode):
    cz = CustomizeCommitsCz(config_with_unicode)
    assert cz.change_type_map == {"✨ feature": "Feat", "🐛 bug fix": "Fix"}
