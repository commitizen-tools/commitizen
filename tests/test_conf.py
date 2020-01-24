import os
from pathlib import Path

import pytest

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

[tool.black]
line-length = 88
target-version = ['py36', 'py37', 'py38']
"""

RAW_CONFIG = """
[commitizen]
name = cz_jira
version = 1.0.0
version_files = [
    "commitizen/__version__.py",
    "pyproject.toml"
    ]
style = [
    ["pointer", "reverse"],
    ["question", "underline"]
    ]
"""

_settings = {
    "name": "cz_jira",
    "version": "1.0.0",
    "tag_format": None,
    "bump_message": None,
    "version_files": ["commitizen/__version__.py", "pyproject.toml"],
    "style": [["pointer", "reverse"], ["question", "underline"]],
    "changelog_file": "CHANGELOG.md",
}

_new_settings = {
    "name": "cz_jira",
    "version": "2.0.0",
    "tag_format": None,
    "bump_message": None,
    "version_files": ["commitizen/__version__.py", "pyproject.toml"],
    "style": [["pointer", "reverse"], ["question", "underline"]],
    "changelog_file": "CHANGELOG.md",
}

_read_settings = {
    "name": "cz_jira",
    "version": "1.0.0",
    "version_files": ["commitizen/__version__.py", "pyproject.toml"],
    "style": [["pointer", "reverse"], ["question", "underline"]],
    "changelog_file": "CHANGELOG.md",
}


@pytest.fixture
def configure_supported_files():
    original = defaults.config_files.copy()

    # patch the defaults to include tests
    defaults.config_files = [os.path.join("tests", f) for f in defaults.config_files]
    yield
    defaults.config_files = original


@pytest.fixture
def config_files_manager(request):
    filename = request.param
    filepath = os.path.join("tests", filename)
    with open(filepath, "w") as f:
        if "toml" in filename:
            f.write(PYPROJECT)
        else:
            f.write(RAW_CONFIG)
    yield
    os.remove(filepath)


@pytest.fixture
def empty_pyproject_ok_cz():
    pyproject = "tests/pyproject.toml"
    cz = "tests/.cz"
    with open(pyproject, "w") as f:
        f.write("")
    with open(cz, "w") as f:
        f.write(RAW_CONFIG)
    yield
    os.remove(pyproject)
    os.remove(cz)


@pytest.mark.parametrize(
    "config_files_manager", defaults.config_files.copy(), indirect=True
)
def test_load_conf(config_files_manager, configure_supported_files):
    cfg = config.read_cfg()
    assert cfg.settings == _settings


def test_conf_is_loaded_with_empty_pyproject_but_ok_cz(
    empty_pyproject_ok_cz, configure_supported_files
):
    cfg = config.read_cfg()
    assert cfg.settings == _settings


def test_conf_returns_default_when_no_files(configure_supported_files):
    cfg = config.read_cfg()
    assert cfg.settings == defaults.DEFAULT_SETTINGS


@pytest.mark.parametrize(
    "config_files_manager", defaults.config_files.copy(), indirect=True
)
def test_set_key(configure_supported_files, config_files_manager):
    _conf = config.read_cfg()
    _conf.set_key("version", "2.0.0")
    cfg = config.read_cfg()
    assert cfg.settings == _new_settings


def test_find_git_project_root(tmpdir):
    assert git.find_git_project_root() == Path(os.getcwd())

    with tmpdir.as_cwd() as _:
        assert git.find_git_project_root() is None


def test_read_cfg_when_not_in_a_git_project(tmpdir):
    with tmpdir.as_cwd() as _:
        with pytest.raises(SystemExit):
            config.read_cfg()


class TestTomlConfig:
    def test_init_empty_config_file(self, tmpdir):
        path = tmpdir.mkdir("commitizen").join(".cz.toml")
        toml_config = config.TomlConfig(data="", path=path)
        toml_config.init_empty_config_file()

        with open(path, "r") as toml_file:
            assert toml_file.read() == "[tool.commitizen]"
