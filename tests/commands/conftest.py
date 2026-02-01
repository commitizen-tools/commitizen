import os
from pathlib import Path

import pytest
from pytest_mock import MockerFixture, MockType

from commitizen.config.json_config import JsonConfig


@pytest.fixture
def config_customize() -> JsonConfig:
    json_string = r"""{
      "commitizen": {
        "name": "cz_customize",
        "version": "3.0.0",
        "changelog_incremental": "true",
        "customize": {
          "message_template": "{{prefix}}({{scope}}): {{subject}}\n\n{{body}}{% if is_breaking_change %}\nBREAKING CHANGE: {{footer}}{% endif %}",
          "schema": "<type>(<scope>): <subject>\n<BLANK LINE>\n<body>\n<BLANK LINE>\n(BREAKING CHANGE: <footer>)",
          "schema_pattern": "(build|ci|docs|feat|fix|perf|refactor|style|test|chore|revert|bump)(\\(\\S+\\))?!?:(\\s.*)",
          "change_type_map": {
            "feat": "Feat",
            "fix": "Fix",
            "refactor": "Refactor",
            "perf": "Perf"
          },
          "change_type_order": ["Refactor", "Feat"],
          "commit_parser": "^(?P<change_type>feat|fix|refactor|perf|BREAKING CHANGE)(?:\\((?P<scope>[^()\\r\\n]*)\\)|\\()?(?P<breaking>!)?:\\s(?P<message>.*)?",
          "changelog_pattern": "^(BREAKING[\\-\\ ]CHANGE|feat|fix|refactor|perf)(\\(.+\\))?(!)?",
          "questions": [

          ]
        }
      }
    }"""
    return JsonConfig(data=json_string, path=Path("not_exist.json"))


@pytest.fixture
def changelog_path() -> str:
    return os.path.join(os.getcwd(), "CHANGELOG.md")


@pytest.fixture
def success_mock(mocker: MockerFixture) -> MockType:
    return mocker.patch("commitizen.out.success")
