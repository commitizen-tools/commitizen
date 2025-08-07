import pytest

from commitizen.config import JsonConfig, TomlConfig, YAMLConfig
from commitizen.cz.conventional_commits import ConventionalCommitsCz

TOML_STR = r"""
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
    name = "message"
    message = "Body."

    [[tool.commitizen.customize.questions]]
    type = "confirm"
    name = "show_message"
    message = "Do you want to add body message in commit?"
"""

JSON_STR = r"""
    {
        "commitizen": {
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

YAML_STR = """
commitizen:
  version: 1.0.0
  version_files:
  - commitizen/__version__.py
  - pyproject.toml
  customize:
    message_template: "{{change_type}}:{% if show_message %} {{message}}{% endif %}"
    example: 'feature: this feature enables customization through a config file'
    schema: "<type>: <body>"
    schema_pattern: "(feature|bug fix):(\\s.*)"
    bump_pattern: "^(break|new|fix|hotfix)"
    bump_map:
      break: MAJOR
      new: MINOR
      fix: PATCH
      hotfix: PATCH
    change_type_order: ["perf", "BREAKING CHANGE", "feat", "fix", "refactor"]
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
      name: message
      message: Body.
    - type: confirm
      name: show_message
      message: Do you want to add body message in commit?
"""

TOML_WITH_UNICODE = r"""
    [tool.commitizen]
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


@pytest.fixture(
    params=[
        TomlConfig(data=TOML_STR, path="not_exist.toml"),
        JsonConfig(data=JSON_STR, path="not_exist.json"),
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
        TomlConfig(data=TOML_STR_INFO_PATH, path="not_exist.toml"),
        JsonConfig(data=JSON_STR_INFO_PATH, path="not_exist.json"),
        YAMLConfig(data=YAML_STR_INFO_PATH, path="not_exist.yaml"),
    ]
)
def config_info(request):
    return request.param


@pytest.fixture(
    params=[
        TomlConfig(data=TOML_WITH_UNICODE, path="not_exist.toml"),
        JsonConfig(data=JSON_WITH_UNICODE, path="not_exist.json"),
    ]
)
def config_with_unicode(request):
    return request.param


def test_bump_pattern(config):
    cz = ConventionalCommitsCz(config)
    assert cz.bump_pattern == "^(break|new|fix|hotfix)"


def test_bump_pattern_unicode(config_with_unicode):
    cz = ConventionalCommitsCz(config_with_unicode)
    assert cz.bump_pattern == "^(✨ feat|🐛 bug fix)"


def test_bump_map(config):
    cz = ConventionalCommitsCz(config)
    assert cz.bump_map == {
        "break": "MAJOR",
        "new": "MINOR",
        "fix": "PATCH",
        "hotfix": "PATCH",
    }


def test_bump_map_unicode(config_with_unicode):
    cz = ConventionalCommitsCz(config_with_unicode)
    assert cz.bump_map == {
        "break": "MAJOR",
        "✨ feat": "MINOR",
        "🐛 bug fix": "MINOR",
    }


def test_change_type_order(config):
    cz = ConventionalCommitsCz(config)
    assert cz.change_type_order == [
        "perf",
        "BREAKING CHANGE",
        "feat",
        "fix",
        "refactor",
    ]


def test_change_type_order_unicode(config_with_unicode):
    cz = ConventionalCommitsCz(config_with_unicode)
    assert cz.change_type_order == [
        "perf",
        "BREAKING CHANGE",
        "feat",
        "fix",
        "refactor",
    ]


def test_questions(config):
    cz = ConventionalCommitsCz(config)
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


def test_questions_unicode(config_with_unicode):
    cz = ConventionalCommitsCz(config_with_unicode)
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
    cz = ConventionalCommitsCz(config)
    answers = {
        "change_type": "feature",
        "message": "this feature enable customize through config file",
        "show_message": True,
    }
    message = cz.message(answers)
    assert message == "feature: this feature enable customize through config file"

    cz = ConventionalCommitsCz(config)
    answers = {
        "change_type": "feature",
        "message": "this feature enable customize through config file",
        "show_message": False,
    }
    message = cz.message(answers)
    assert message == "feature:"


def test_answer_unicode(config_with_unicode):
    cz = ConventionalCommitsCz(config_with_unicode)
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

    cz = ConventionalCommitsCz(config_with_unicode)
    answers = {
        "change_type": "✨ feature",
        "message": "this feature enables customization through a config file",
        "show_message": False,
    }
    message = cz.message(answers)
    assert message == "✨ feature:"


def test_example(config):
    cz = ConventionalCommitsCz(config)
    assert (
        "feature: this feature enables customization through a config file"
        in cz.example()
    )


def test_example_unicode(config_with_unicode):
    cz = ConventionalCommitsCz(config_with_unicode)
    assert (
        "✨ feature: this feature enables customization through a config file"
        in cz.example()
    )


def test_schema(config):
    cz = ConventionalCommitsCz(config)
    assert "<type>: <body>" in cz.schema()


def test_schema_pattern(config):
    cz = ConventionalCommitsCz(config)
    assert r"(feature|bug fix):(\s.*)" in cz.schema_pattern()


def test_schema_pattern_unicode(config_with_unicode):
    cz = ConventionalCommitsCz(config_with_unicode)
    assert r"(✨ feature|🐛 bug fix):(\s.*)" in cz.schema_pattern()


def test_info(config):
    cz = ConventionalCommitsCz(config)
    assert "This is a customized cz." in cz.info()


def test_info_unicode(config_with_unicode):
    cz = ConventionalCommitsCz(config_with_unicode)
    assert "This is a customized cz with emojis 🎉!" in cz.info()


def test_info_with_info_path(tmpdir, config_info):
    with tmpdir.as_cwd():
        tmpfile = tmpdir.join("info.txt")
        tmpfile.write("Test info")

        cz = ConventionalCommitsCz(config_info)
        assert "Test info" in cz.info()


def test_commit_parser(config):
    cz = ConventionalCommitsCz(config)
    assert cz.commit_parser == "^(?P<change_type>feature|bug fix):\\s(?P<message>.*)?"


def test_commit_parser_unicode(config_with_unicode):
    cz = ConventionalCommitsCz(config_with_unicode)
    assert (
        cz.commit_parser
        == "^(?P<change_type>✨ feature|🐛 bug fix):\\s(?P<message>.*)?"
    )


def test_changelog_pattern(config):
    cz = ConventionalCommitsCz(config)
    assert cz.changelog_pattern == "^(feature|bug fix)?(!)?"


def test_changelog_pattern_unicode(config_with_unicode):
    cz = ConventionalCommitsCz(config_with_unicode)
    assert cz.changelog_pattern == "^(✨ feature|🐛 bug fix)?(!)?"


def test_change_type_map(config):
    cz = ConventionalCommitsCz(config)
    assert cz.change_type_map == {"feature": "Feat", "bug fix": "Fix"}


def test_change_type_map_unicode(config_with_unicode):
    cz = ConventionalCommitsCz(config_with_unicode)
    assert cz.change_type_map == {"✨ feature": "Feat", "🐛 bug fix": "Fix"}
