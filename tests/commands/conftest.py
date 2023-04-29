import os
from pathlib import Path
from typing import NamedTuple

import pytest

from commitizen import defaults
from commitizen.config import BaseConfig, JsonConfig


@pytest.fixture()
def config():
    _config = BaseConfig()
    _config.settings.update({"name": defaults.DEFAULT_SETTINGS["name"]})
    return _config


@pytest.fixture()
def config_customize():
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
    _config = JsonConfig(data=json_string, path="not_exist.json")
    return _config


class Plugin(NamedTuple):
    name: str
    extension: str

    @property
    def changelog_file(self) -> str:
        return f"CHANGELOG{self.extension}"

    @property
    def template(self) -> str:
        return f"CHANGELOG{self.extension}.j2"

    @property
    def cli_args(self):
        return ["--file-name", self.changelog_file, "--template", self.template]


TESTED_PLUGINS = {
    "Markdown": Plugin("cz_conventional_commits", ".md"),
    "Textile": Plugin("conventional_commits_textile", ".textile"),
    "AsciiDoc": Plugin("conventional_commits_asciidoc", ".adoc"),
    "RestructuredText": Plugin("conventional_commits_restructuredtext", ".rst"),
}


@pytest.fixture(
    params=[pytest.param(plugin, id=id) for id, plugin in TESTED_PLUGINS.items()]
)
def plugin(
    config: BaseConfig,
    request: pytest.FixtureRequest,
    tmp_commitizen_project: Path,
) -> Plugin:
    plugin: Plugin = request.param
    config.settings["name"] = plugin.name
    config.settings["changelog_file"] = plugin.changelog_file
    with (tmp_commitizen_project / "pyproject.toml").open("a") as cfg:
        cfg.write(f'name="{plugin.name}"')
    return plugin


@pytest.fixture()
def changelog_path() -> str:
    return os.path.join(os.getcwd(), "CHANGELOG.md")


@pytest.fixture()
def config_path() -> str:
    return os.path.join(os.getcwd(), "pyproject.toml")
