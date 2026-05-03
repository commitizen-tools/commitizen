from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest
import yaml

from commitizen import cmd, config, defaults, git
from commitizen.config.json_config import JsonConfig
from commitizen.config.toml_config import TomlConfig
from commitizen.config.yaml_config import YAMLConfig
from commitizen.exceptions import ConfigFileIsEmpty, InvalidConfigurationError

TOML_STR = """
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
"""

PYPROJECT = f"""
{TOML_STR}

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

JSON_STR = r"""
    {
        "commitizen": {
            "name": "cz_jira",
            "version": "1.0.0",
            "version_files": [
                "commitizen/__version__.py",
                "pyproject.toml"
            ]
        }
    }
"""

YAML_STR = """
commitizen:
  name: cz_jira
  version: 1.0.0
  version_files:
  - commitizen/__version__.py
  - pyproject.toml
"""

_settings: dict[str, Any] = {
    "name": "cz_jira",
    "version": "1.0.0",
    "version_provider": "commitizen",
    "version_scheme": None,
    "tag_format": "$version",
    "legacy_tag_formats": [],
    "ignored_tag_formats": [],
    "bump_message": None,
    "retry_after_failure": False,
    "allow_abort": False,
    "allowed_prefixes": [
        "Merge",
        "Revert",
        "Pull request",
        "fixup!",
        "squash!",
        "amend!",
    ],
    "version_files": ["commitizen/__version__.py", "pyproject.toml"],
    "style": [["pointer", "reverse"], ["question", "underline"]],
    "changelog_file": "CHANGELOG.md",
    "changelog_format": None,
    "changelog_incremental": False,
    "changelog_start_rev": None,
    "changelog_merge_prerelease": False,
    "update_changelog_on_bump": False,
    "use_shortcuts": False,
    "major_version_zero": False,
    "pre_bump_hooks": ["scripts/generate_documentation.sh"],
    "post_bump_hooks": ["scripts/slack_notification.sh"],
    "prerelease_offset": 0,
    "encoding": "utf-8",
    "always_signoff": False,
    "template": None,
    "extras": {},
    "breaking_change_exclamation_in_title": False,
    "message_length_limit": 0,
}

_new_settings: dict[str, Any] = {
    "name": "cz_jira",
    "version": "2.0.0",
    "version_provider": "commitizen",
    "version_scheme": None,
    "tag_format": "$version",
    "legacy_tag_formats": [],
    "ignored_tag_formats": [],
    "bump_message": None,
    "retry_after_failure": False,
    "allow_abort": False,
    "allowed_prefixes": [
        "Merge",
        "Revert",
        "Pull request",
        "fixup!",
        "squash!",
        "amend!",
    ],
    "version_files": ["commitizen/__version__.py", "pyproject.toml"],
    "style": [["pointer", "reverse"], ["question", "underline"]],
    "changelog_file": "CHANGELOG.md",
    "changelog_format": None,
    "changelog_incremental": False,
    "changelog_start_rev": None,
    "changelog_merge_prerelease": False,
    "update_changelog_on_bump": False,
    "use_shortcuts": False,
    "major_version_zero": False,
    "pre_bump_hooks": ["scripts/generate_documentation.sh"],
    "post_bump_hooks": ["scripts/slack_notification.sh"],
    "prerelease_offset": 0,
    "encoding": "utf-8",
    "always_signoff": False,
    "template": None,
    "extras": {},
    "breaking_change_exclamation_in_title": False,
    "message_length_limit": 0,
}


@pytest.fixture
def config_files_manager(request, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    filename = request.param
    path = tmp_path / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        if "toml" in filename:
            f.write(PYPROJECT)
        elif "json" in filename:
            json.dump(DICT_CONFIG, f)
        elif "yaml" in filename:
            yaml.dump(DICT_CONFIG, f)
    return


@pytest.mark.usefixtures("in_repo_root")
def test_find_git_project_root(tmp_path, monkeypatch):
    assert git.find_git_project_root() == Path(os.getcwd())

    monkeypatch.chdir(tmp_path)
    assert git.find_git_project_root() is None


@pytest.mark.parametrize("config_files_manager", defaults.CONFIG_FILES, indirect=True)
def test_set_key(config_files_manager):
    _conf = config.read_cfg()
    _conf.set_key("version", "2.0.0")
    cfg = config.read_cfg()
    assert cfg.settings == _new_settings


class TestReadCfg:
    @pytest.mark.parametrize(
        "config_files_manager", defaults.CONFIG_FILES, indirect=True
    )
    def test_load_conf(self, config_files_manager):
        cfg = config.read_cfg()
        assert cfg.settings == _settings

    def test_conf_returns_default_when_no_files(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = config.read_cfg()
        assert cfg.settings == defaults.DEFAULT_SETTINGS

    def test_load_empty_pyproject_toml_and_cz_toml_with_config(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "pyproject.toml").write_text("")
        (tmp_path / ".cz.toml").write_text(TOML_STR)

        cfg = config.read_cfg()
        assert cfg.settings == _settings

    def test_load_pyproject_toml_from_config_argument(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _not_root_path = tmp_path / "not_in_root" / "pyproject.toml"
        _not_root_path.parent.mkdir(parents=True, exist_ok=True)
        _not_root_path.write_text(PYPROJECT)

        cfg = config.read_cfg(_not_root_path)
        assert cfg.settings == _settings

    def test_load_cz_json_not_from_config_argument(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _not_root_path = tmp_path / "not_in_root" / ".cz.json"
        _not_root_path.parent.mkdir(parents=True, exist_ok=True)
        _not_root_path.write_text(JSON_STR)

        cfg = config.read_cfg(_not_root_path)
        json_cfg_by_class = JsonConfig(data=JSON_STR, path=_not_root_path)
        assert cfg.settings == json_cfg_by_class.settings

    def test_load_cz_yaml_not_from_config_argument(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _not_root_path = tmp_path / "not_in_root" / ".cz.yaml"
        _not_root_path.parent.mkdir(parents=True, exist_ok=True)
        _not_root_path.write_text(YAML_STR)

        cfg = config.read_cfg(_not_root_path)
        yaml_cfg_by_class = YAMLConfig(data=YAML_STR, path=_not_root_path)
        assert cfg.settings == yaml_cfg_by_class._settings

    def test_load_empty_pyproject_toml_from_config_argument(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        _not_root_path = tmp_path / "not_in_root" / "pyproject.toml"
        _not_root_path.parent.mkdir(parents=True, exist_ok=True)
        _not_root_path.write_text("")

        with pytest.raises(ConfigFileIsEmpty):
            config.read_cfg(_not_root_path)

    def test_load_empty_json_from_config_argument(self, tmpdir):
        with tmpdir.as_cwd():
            _not_root_path = tmpdir.mkdir("not_in_root").join(".cz.json")
            _not_root_path.write("")

            with pytest.raises(ConfigFileIsEmpty):
                config.read_cfg(filepath="./not_in_root/.cz.json")

    def test_load_empty_yaml_from_config_argument(self, tmpdir):
        with tmpdir.as_cwd():
            _not_root_path = tmpdir.mkdir("not_in_root").join(".cz.yaml")
            _not_root_path.write("")

            with pytest.raises(ConfigFileIsEmpty):
                config.read_cfg(filepath="./not_in_root/.cz.yaml")


class TestWarnMultipleConfigFiles:
    @pytest.mark.parametrize(
        ("files", "expected_path"),
        [
            # Same directory, different file types
            ([(".cz.toml", TOML_STR), (".cz.json", JSON_STR)], ".cz.toml"),
            ([(".cz.json", JSON_STR), (".cz.yaml", YAML_STR)], ".cz.json"),
            ([(".cz.toml", TOML_STR), (".cz.yaml", YAML_STR)], ".cz.toml"),
            # With pyproject.toml
            (
                [("pyproject.toml", PYPROJECT), (".cz.json", JSON_STR)],
                ".cz.json",
            ),
            (
                [("pyproject.toml", PYPROJECT), (".cz.toml", TOML_STR)],
                ".cz.toml",
            ),
        ],
    )
    def test_warn_multiple_config_files_same_dir(
        self, tmp_path, monkeypatch, capsys, files, expected_path
    ):
        """Test warning when multiple config files exist in same directory."""
        monkeypatch.chdir(tmp_path)
        for filename, content in files:
            (tmp_path / filename).write_text(content)

        cfg = config.read_cfg()
        captured = capsys.readouterr()

        assert "Multiple config files detected" in captured.err
        for filename, _ in files:
            assert filename in captured.err
        assert f"Using config file: '{expected_path}'" in captured.err

        assert cfg.path == Path(expected_path)

    @pytest.mark.parametrize(
        ("config_file", "content"),
        [
            (".cz.json", JSON_STR),
            (".cz.toml", TOML_STR),
            (".cz.yaml", YAML_STR),
            ("cz.toml", TOML_STR),
            ("cz.json", JSON_STR),
            ("cz.yaml", YAML_STR),
        ],
    )
    def test_warn_same_filename_different_directories_with_git(
        self, tmp_path, monkeypatch, capsys, config_file, content
    ):
        """Test warning when same config filename exists in the current directory and in the git root."""
        monkeypatch.chdir(tmp_path)
        cmd.run("git init")

        # Create config in git root
        (tmp_path / config_file).write_text(content)

        # Create same filename in subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / config_file).write_text(content)

        monkeypatch.chdir(subdir)
        cfg = config.read_cfg()
        captured = capsys.readouterr()

        assert "Multiple config files detected" in captured.err
        assert f"Using config file: '{config_file}'" in captured.err
        assert cfg.path == Path(config_file)

    def test_no_warn_with_explicit_config_path(self, tmp_path, monkeypatch, capsys):
        """Test that no warning is issued when user explicitly specifies config."""
        monkeypatch.chdir(tmp_path)
        # Create multiple config files
        (tmp_path / ".cz.toml").write_text(PYPROJECT)
        (tmp_path / ".cz.json").write_text(JSON_STR)

        # Read config with explicit path
        cfg = config.read_cfg(Path(".cz.json"))

        # No warning should be issued
        captured = capsys.readouterr()
        assert "Multiple config files detected" not in captured.err

        # Verify the explicitly specified config is loaded (compare to expected JSON config)
        json_cfg_expected = JsonConfig(data=JSON_STR, path=Path(".cz.json"))
        assert cfg.settings == json_cfg_expected.settings

    @pytest.mark.parametrize(
        ("config_file", "content", "with_git"),
        [
            (file, content, with_git)
            for file, content in [
                (".cz.toml", TOML_STR),
                (".cz.json", JSON_STR),
                (".cz.yaml", YAML_STR),
                ("pyproject.toml", PYPROJECT),
                ("cz.toml", TOML_STR),
                ("cz.json", JSON_STR),
                ("cz.yaml", YAML_STR),
            ]
            for with_git in [True, False]
        ],
    )
    def test_no_warn_with_single_config_file(
        self, tmp_path, monkeypatch, capsys, config_file, content, with_git
    ):
        """Test that no warning is issued when user explicitly specifies config."""
        monkeypatch.chdir(tmp_path)
        if with_git:
            cmd.run("git init")

        (tmp_path / config_file).write_text(content)

        cfg = config.read_cfg()
        captured = capsys.readouterr()

        # No warning should be issued
        assert "Multiple config files detected" not in captured.err
        assert cfg.path == Path(config_file)

    def test_no_warn_with_no_commitizen_section_in_pyproject_toml_and_cz_toml(
        self, tmp_path, monkeypatch, capsys
    ):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "pyproject.toml").write_text("[tool.foo]\nbar = 'baz'")
        (tmp_path / ".cz.toml").write_text(TOML_STR)

        cfg = config.read_cfg()
        captured = capsys.readouterr()
        assert "Multiple config files detected" not in captured.err
        assert cfg.path == Path(".cz.toml")


@pytest.mark.parametrize(
    "config_file",
    [
        ".cz.toml",
        "cz.toml",
        "pyproject.toml",
    ],
)
class TestTomlConfig:
    def test_init_empty_config_content(self, tmp_path, config_file):
        path = tmp_path / "commitizen" / config_file
        path.parent.mkdir(parents=True, exist_ok=True)
        toml_config = TomlConfig(data="", path=path)
        toml_config.init_empty_config_content()

        assert path.read_text(encoding="utf-8") == "[tool.commitizen]\n"

    def test_init_empty_config_content_with_existing_content(
        self, tmp_path, config_file
    ):
        existing_content = "[tool.black]\nline-length = 88\n"

        path = tmp_path / "commitizen" / config_file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(existing_content)
        toml_config = TomlConfig(data="", path=path)
        toml_config.init_empty_config_content()

        assert (
            path.read_text(encoding="utf-8")
            == existing_content + "\n[tool.commitizen]\n"
        )

    def test_init_with_invalid_config_content(self, tmp_path, config_file):
        existing_content = "invalid toml content"
        path = tmp_path / "commitizen" / config_file
        path.parent.mkdir(parents=True, exist_ok=True)

        with pytest.raises(InvalidConfigurationError) as excinfo:
            TomlConfig(data=existing_content, path=path)
        assert config_file in str(excinfo.value)


@pytest.mark.parametrize(
    "config_file",
    [
        ".cz.json",
        "cz.json",
    ],
)
class TestJsonConfig:
    def test_init_empty_config_content(self, tmp_path, config_file):
        path = tmp_path / "commitizen" / config_file
        path.parent.mkdir(parents=True, exist_ok=True)
        json_config = JsonConfig(data="{}", path=path)
        json_config.init_empty_config_content()

        with path.open(encoding="utf-8") as json_file:
            assert json.load(json_file) == {"commitizen": {}}

    def test_init_with_invalid_config_content(self, tmp_path, config_file):
        existing_content = "invalid json content"
        path = tmp_path / "commitizen" / config_file
        path.parent.mkdir(parents=True, exist_ok=True)

        with pytest.raises(InvalidConfigurationError) as excinfo:
            JsonConfig(data=existing_content, path=path)
        assert config_file in str(excinfo.value)


@pytest.mark.parametrize(
    "config_file",
    [
        ".cz.yaml",
        "cz.yaml",
    ],
)
class TestYamlConfig:
    def test_init_empty_config_content(self, tmp_path, config_file):
        path = tmp_path / "commitizen" / config_file
        path.parent.mkdir(parents=True, exist_ok=True)
        yaml_config = YAMLConfig(data="{}", path=path)
        yaml_config.init_empty_config_content()

        with path.open() as yaml_file:
            assert yaml.safe_load(yaml_file) == {"commitizen": {}}

    def test_init_with_invalid_content(self, tmp_path, config_file):
        existing_content = "invalid: .cz.yaml: content: maybe?"
        path = tmp_path / "commitizen" / config_file
        path.parent.mkdir(parents=True, exist_ok=True)

        with pytest.raises(InvalidConfigurationError) as excinfo:
            YAMLConfig(data=existing_content, path=path)
        assert config_file in str(excinfo.value)
