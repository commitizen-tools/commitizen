import json
import os
from pathlib import Path

import pytest
import yaml

from commitizen import config, defaults, git

PYPROJECT = """
[tool.commitizen]
name = "cz_jira"
version = "1.0.0"
version_files = [
    "commitizen/__version__.py",
    "pyproject.toml"
]
style = [
    ["pointer", "reverse"],
    ["question", "underline"]
]
pre_bump_hooks = [
    "scripts/generate_documentation.sh"
]
post_bump_hooks = ["scripts/slack_notification.sh"]

[tool.black]
line-length = 88
target-version = ['py36', 'py37', 'py38']
"""

DICT_CONFIG = {
    "commitizen": {
        "name": "cz_jira",
        "version": "1.0.0",
        "version_files": ["commitizen/__version__.py", "pyproject.toml"],
        "style": [["pointer", "reverse"], ["question", "underline"]],
        "pre_bump_hooks": ["scripts/generate_documentation.sh"],
        "post_bump_hooks": ["scripts/slack_notification.sh"],
    }
}


_settings = {
    "name": "cz_jira",
    "version": "1.0.0",
    "tag_format": None,
    "bump_message": None,
    "allow_abort": False,
    "version_files": ["commitizen/__version__.py", "pyproject.toml"],
    "style": [["pointer", "reverse"], ["question", "underline"]],
    "changelog_file": "CHANGELOG.md",
    "changelog_incremental": False,
    "changelog_start_rev": None,
    "update_changelog_on_bump": False,
    "use_shortcuts": False,
    "major_version_zero": False,
    "pre_bump_hooks": ["scripts/generate_documentation.sh"],
    "post_bump_hooks": ["scripts/slack_notification.sh"],
    "prerelease_offset": 0,
}

_new_settings = {
    "name": "cz_jira",
    "version": "2.0.0",
    "tag_format": None,
    "bump_message": None,
    "allow_abort": False,
    "version_files": ["commitizen/__version__.py", "pyproject.toml"],
    "style": [["pointer", "reverse"], ["question", "underline"]],
    "changelog_file": "CHANGELOG.md",
    "changelog_incremental": False,
    "changelog_start_rev": None,
    "update_changelog_on_bump": False,
    "use_shortcuts": False,
    "major_version_zero": False,
    "pre_bump_hooks": ["scripts/generate_documentation.sh"],
    "post_bump_hooks": ["scripts/slack_notification.sh"],
    "prerelease_offset": 0,
}

_read_settings = {
    "name": "cz_jira",
    "version": "1.0.0",
    "version_files": ["commitizen/__version__.py", "pyproject.toml"],
    "style": [["pointer", "reverse"], ["question", "underline"]],
    "changelog_file": "CHANGELOG.md",
    "pre_bump_hooks": ["scripts/generate_documentation.sh"],
    "post_bump_hooks": ["scripts/slack_notification.sh"],
}


@pytest.fixture
def config_files_manager(request, tmpdir):
    with tmpdir.as_cwd():
        filename = request.param
        with open(filename, "w") as f:
            if "toml" in filename:
                f.write(PYPROJECT)
            elif "json" in filename:
                json.dump(DICT_CONFIG, f)
            elif "yaml" in filename:
                yaml.dump(DICT_CONFIG, f)
        yield


def test_find_git_project_root(tmpdir):
    assert git.find_git_project_root() == Path(os.getcwd())

    with tmpdir.as_cwd() as _:
        assert git.find_git_project_root() is None


@pytest.mark.parametrize(
    "config_files_manager", defaults.config_files.copy(), indirect=True
)
def test_set_key(config_files_manager):
    _conf = config.read_cfg()
    _conf.set_key("version", "2.0.0")
    cfg = config.read_cfg()
    assert cfg.settings == _new_settings


class TestReadCfg:
    @pytest.mark.parametrize(
        "config_files_manager", defaults.config_files.copy(), indirect=True
    )
    def test_load_conf(_, config_files_manager):
        cfg = config.read_cfg()
        assert cfg.settings == _settings

    def test_conf_returns_default_when_no_files(_, tmpdir):
        with tmpdir.as_cwd():
            cfg = config.read_cfg()
            assert cfg.settings == defaults.DEFAULT_SETTINGS

    def test_load_empty_pyproject_toml_and_cz_toml_with_config(_, tmpdir):
        with tmpdir.as_cwd():
            p = tmpdir.join("pyproject.toml")
            p.write("")
            p = tmpdir.join(".cz.toml")
            p.write(PYPROJECT)

            cfg = config.read_cfg()
            assert cfg.settings == _settings


class TestTomlConfig:
    def test_init_empty_config_content(self, tmpdir):
        path = tmpdir.mkdir("commitizen").join(".cz.toml")
        toml_config = config.TomlConfig(data="", path=path)
        toml_config.init_empty_config_content()

        with open(path, "r") as toml_file:
            assert toml_file.read() == "[tool.commitizen]\n"

    def test_init_empty_config_content_with_existing_content(self, tmpdir):
        existing_content = "[tool.black]\n" "line-length = 88\n"

        path = tmpdir.mkdir("commitizen").join(".cz.toml")
        path.write(existing_content)
        toml_config = config.TomlConfig(data="", path=path)
        toml_config.init_empty_config_content()

        with open(path, "r") as toml_file:
            assert toml_file.read() == existing_content + "\n[tool.commitizen]\n"


class TestJsonConfig:
    def test_init_empty_config_content(self, tmpdir):
        path = tmpdir.mkdir("commitizen").join(".cz.json")
        json_config = config.JsonConfig(data="{}", path=path)
        json_config.init_empty_config_content()

        with open(path, "r") as json_file:
            assert json.load(json_file) == {"commitizen": {}}


class TestYamlConfig:
    def test_init_empty_config_content(self, tmpdir):
        path = tmpdir.mkdir("commitizen").join(".cz.yaml")
        yaml_config = config.YAMLConfig(data="{}", path=path)
        yaml_config.init_empty_config_content()

        with open(path, "r") as yaml_file:
            assert yaml.safe_load(yaml_file) == {"commitizen": {}}
