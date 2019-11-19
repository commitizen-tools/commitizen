import os

import pytest

from commitizen import config, defaults

PYPROJECT = """
[tool.commitizen]
name = "cz_jira"
version = "1.0.0"
files = [
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
files = [
    "commitizen/__version__.py",
    "pyproject.toml"
    ]
style = [
    ["pointer", "reverse"],
    ["question", "underline"]
    ]
"""

_config = {
    "name": "cz_jira",
    "version": "1.0.0",
    "tag_format": None,
    "bump_message": None,
    "files": ["commitizen/__version__.py", "pyproject.toml"],
    "style": [["pointer", "reverse"], ["question", "underline"]],
}

_new_config = {
    "name": "cz_jira",
    "version": "2.0.0",
    "tag_format": None,
    "bump_message": None,
    "files": ["commitizen/__version__.py", "pyproject.toml"],
    "style": [["pointer", "reverse"], ["question", "underline"]],
}

_read_conf = {
    "name": "cz_jira",
    "version": "1.0.0",
    "files": ["commitizen/__version__.py", "pyproject.toml"],
    "style": [["pointer", "reverse"], ["question", "underline"]],
}


@pytest.fixture
def configure_supported_files():
    config._conf = config.Config()
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


def test_read_pyproject_conf():
    assert config.read_pyproject_conf(PYPROJECT) == _read_conf


def test_read_pyproject_conf_empty():
    assert config.read_pyproject_conf("") == {}


def test_read_raw_parser_conf():
    assert config.read_raw_parser_conf(RAW_CONFIG) == _read_conf


def test_read_raw_parser_conf_empty():
    assert config.read_raw_parser_conf("") == {}


@pytest.mark.parametrize(
    "config_files_manager", defaults.config_files.copy(), indirect=True
)
def test_load_conf(config_files_manager, configure_supported_files):
    cfg = config.read_cfg()
    assert cfg == _config


def test_conf_is_loaded_with_empty_pyproject_but_ok_cz(
    empty_pyproject_ok_cz, configure_supported_files
):
    cfg = config.read_cfg()
    assert cfg == _config


def test_conf_returns_default_when_no_files(configure_supported_files):
    cfg = config.read_cfg()
    assert cfg == defaults.settings


@pytest.mark.parametrize(
    "config_files_manager", defaults.config_files.copy(), indirect=True
)
def test_set_key(configure_supported_files, config_files_manager):
    config.read_cfg()
    config.set_key("version", "2.0.0")
    cfg = config.read_cfg()
    assert cfg == _new_config
